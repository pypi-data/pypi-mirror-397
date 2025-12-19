import os
import logging
from typing import Union, List, Optional, Dict
from pathlib import Path

from O365 import Account, FileSystemTokenBackend
from O365.drive import Drive, Folder

from ..exceptions import OneDriveIntegrationError

logger = logging.getLogger(__name__)

class OneDriveProvider:
    """Manages OneDrive and SharePoint operations for document pipelines.
    
    Handles authentication, file uploads/downloads, and directory navigation
    using Microsoft Graph API credentials.
    """

    def __init__(
        self, 
        client_id: str, 
        client_secret: str, 
        tenant_id: str, 
        target_resource_id: str,
        token_path: str = ".",
        is_sharepoint: bool = True
    ):
        """Initialize connection with Microsoft Graph credentials.

        Args:
            client_id: Azure App Client ID.
            client_secret: Azure App Client Secret.
            tenant_id: Azure Directory (Tenant) ID.
            target_resource_id: SharePoint Site ID (if is_sharepoint=True) 
                or User Email (if is_sharepoint=False).
            token_path: Directory path to store the auth token file. 
                Defaults to current directory.
            is_sharepoint: Flag to determine if target is a SharePoint site 
                (True) or User OneDrive (False).

        Raises:
            OneDriveIntegrationError: If credentials are missing or invalid format.
        """
        if not all([client_id, client_secret, tenant_id, target_resource_id]):
            raise OneDriveIntegrationError("Missing required Azure credentials.")

        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.target_resource_id = target_resource_id
        self.is_sharepoint = is_sharepoint
        
        self.token_backend = FileSystemTokenBackend(
            token_path=token_path, 
            token_filename='o365_token.txt'
        )
        
        self.account = self._authenticate()
        self.drive = self._get_drive_instance()

    def _authenticate(self) -> Account:
        """Internal method to authenticate via Client Credentials flow."""
        try:
            credentials = (self.client_id, self.client_secret)
            account = Account(
                credentials, 
                auth_flow_type='credentials', 
                tenant_id=self.tenant_id,
                token_backend=self.token_backend
            )
            
            if not account.authenticate():
                raise OneDriveIntegrationError("Authentication failed with provided credentials.")
            
            return account
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise OneDriveIntegrationError(f"Failed to authenticate: {str(e)}") from e

    def _get_drive_instance(self) -> Drive:
        """Retrieves the target Drive object (SharePoint Library or User Drive)."""
        try:
            if self.is_sharepoint:
                # SharePoint Logic
                site = self.account.sharepoint().get_site(self.target_resource_id)
                # Gets default "Documents" library. 
                return site.get_default_document_library()
            else:
                # User OneDrive Logic
                resource = f'users/{self.target_resource_id}'
                storage = self.account.storage(resource=resource)
                return storage.get_default_drive()

        except Exception as e:
            logger.error(f"Error connecting to Drive resource: {e}")
            raise OneDriveIntegrationError(f"Could not access Drive: {str(e)}") from e

    def _navigate_folder(self, remote_path: str, create_missing: bool = False) -> Folder:
        """Navigates to a specific folder, optionally creating path.

        Args:
            remote_path: Path string (e.g., 'General/Reports/2025').
            create_missing: If True, creates non-existent folders in the path.

        Returns:
            O365 Folder object.

        Raises:
            OneDriveIntegrationError: If folder not found and create_missing is False.
        """
        if not remote_path or remote_path.strip() in ["", "/"]:
            return self.drive.get_root_folder()

        clean_path = remote_path.strip("/").split("/")
        current_folder = self.drive.get_root_folder()

        try:
            for name in clean_path:
                found = False
                # O365 get_items returns a generator, so we must iterate to find the specific folder.
                for item in current_folder.get_items():
                    if item.is_folder and item.name == name:
                        current_folder = item
                        found = True
                        break
                
                if not found:
                    if create_missing:
                        logger.info(f"Creating remote folder: {name}")
                        current_folder = current_folder.create_child_folder(name)
                    else:
                        raise FileNotFoundError(f"Remote folder '{name}' not found in path.")
            
            return current_folder

        except Exception as e:
            raise OneDriveIntegrationError(f"Navigation error at '{remote_path}': {str(e)}") from e

    def _download_recursive(self, remote_folder_obj: Folder, local_base_path: str) -> List[str]:
        """Recursively downloads a remote folder structure to disk.

        Args:
            remote_folder_obj: The O365 Folder instance to download.
            local_base_path: The local directory path where contents will be saved.

        Returns:
            List of strings containing absolute paths of all downloaded files.
        """
        downloaded_paths = []
        
        if not os.path.exists(local_base_path):
            os.makedirs(local_base_path)

        for item in remote_folder_obj.get_items():
            if item.is_file:
                logger.info(f"Downloading file: {item.name}")
                if item.download(to_path=local_base_path):
                    downloaded_paths.append(os.path.abspath(os.path.join(local_base_path, item.name)))
            
            elif item.is_folder:
                new_local_dir = os.path.join(local_base_path, item.name)
                logger.info(f"Processing subfolder: {item.name}")
                downloaded_paths.extend(self._download_recursive(item, new_local_dir))
        
        return downloaded_paths

    def upload_file(
        self, 
        local_path: str, 
        remote_folder: str, 
        rename_to: Optional[str] = None
    ) -> str:
        """Uploads a local file to a specific remote folder.

        Args:
            local_path: Path to the local file.
            remote_folder: Destination path in OneDrive (e.g., 'Docs/Processed').
            rename_to: Optional new name for the file in cloud.

        Returns:
            Web URL of the uploaded file.
        """
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Local file not found: '{local_path}'")

        try:
            target_folder = self._navigate_folder(remote_folder, create_missing=True)
            
            logger.info(f"Uploading '{local_path}' to '{remote_folder}'...")
            # O365 upload method uses the local filename by default.
            new_file = target_folder.upload_file(local_path)
            
            if not new_file:
                raise OneDriveIntegrationError("Upload failed (no object returned).")

            if rename_to:
                new_file.rename(rename_to)
                logger.info(f"Renamed uploaded file to '{rename_to}'")

            return new_file.web_url

        except Exception as e:
            logger.error(f"Upload failed for {local_path}: {e}")
            raise OneDriveIntegrationError(f"Upload failed: {str(e)}") from e

    def download(self, remote_path: str, local_dest: Optional[str] = None) -> Union[str, List[str]]:
        """Downloads a remote file or folder intelligently.

        If the remote path is a folder, it performs a recursive download.
        If the remote path is a file, it downloads the single file.

        Args:
            remote_path: Path to the remote file or folder.
            local_dest: Destination path. 
                - If None: Downloads to current working directory.
                - If downloading a folder: Must be a directory path.
                - If downloading a file: Can be a directory (preserves name) or a full path (renames).

        Returns:
            str: Absolute path of the downloaded file (single file mode).
            List[str]: List of absolute paths of all files (folder mode).

        Raises:
            FileNotFoundError: If the remote path does not exist.
            OneDriveIntegrationError: If download fails.
        """
        try:
            if local_dest is None:
                local_dest = os.getcwd()

            # Identify parent path and item name to locate the object
            path_parts = remote_path.strip("/").split("/")
            item_name = path_parts[-1]
            parent_path = "/".join(path_parts[:-1])

            parent_folder = self._navigate_folder(parent_path, create_missing=False)
            
            target_item = None
            for item in parent_folder.get_items():
                if item.name == item_name:
                    target_item = item
                    break
            
            if not target_item:
                raise FileNotFoundError(f"Remote item '{remote_path}' not found.")

            # --- Case 1: Target is a File ---
            if target_item.is_file:
                # Check if local_dest is a directory or a specific file path
                is_dir = os.path.isdir(local_dest) or (not os.path.splitext(local_dest)[1])
                
                if is_dir:
                    if not os.path.exists(local_dest): os.makedirs(local_dest)
                    target_item.download(to_path=local_dest)
                    return os.path.abspath(os.path.join(local_dest, item_name))
                else:
                    # O365 library does not support "download as" directly.
                    # We must download to the parent dir and then rename locally.
                    dest_dir = os.path.dirname(local_dest)
                    if dest_dir and not os.path.exists(dest_dir): 
                        os.makedirs(dest_dir)
                    
                    target_item.download(to_path=dest_dir if dest_dir else ".")
                    
                    original_download_path = os.path.join(dest_dir if dest_dir else ".", item_name)
                    
                    if os.path.abspath(original_download_path) != os.path.abspath(local_dest):
                        if os.path.exists(local_dest): 
                            os.remove(local_dest) 
                        os.rename(original_download_path, local_dest)
                    
                    return os.path.abspath(local_dest)

            # --- Case 2: Target is a Folder ---
            elif target_item.is_folder:
                logger.info(f"Identified '{item_name}' as a folder. Starting recursive download...")
                final_folder_path = os.path.join(local_dest, item_name)
                return self._download_recursive(target_item, final_folder_path)

        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise OneDriveIntegrationError(f"Download failed for '{remote_path}': {str(e)}") from e

    def list_contents(self, remote_folder: str, recursive: bool = False) -> List[Dict[str, str]]:
        """Lists files and folders in a remote path.

        Args:
            remote_folder: Path to list (e.g., 'General/Inputs').
            recursive: If True, lists all subfolders content.

        Returns:
            List of dicts containing 'name', 'type' (file/folder), and 'web_url'.
        """
        try:
            target_folder = self._navigate_folder(remote_folder, create_missing=False)
            results = []

            def _scan(folder, path_prefix):
                for item in folder.get_items():
                    item_type = 'folder' if item.is_folder else 'file'
                    full_name = f"{path_prefix}/{item.name}" if path_prefix else item.name
                    
                    results.append({
                        'name': item.name,
                        'full_path': full_name,
                        'type': item_type,
                        'web_url': item.web_url,
                        'size_bytes': item.size
                    })

                    if recursive and item.is_folder:
                        _scan(item, full_name)

            _scan(target_folder, "")
            return results

        except Exception as e:
            logger.error(f"Listing failed: {e}")
            raise OneDriveIntegrationError(f"Could not list contents of '{remote_folder}': {str(e)}") from e

    def delete_file(self, remote_file_path: str) -> bool:
        """Deletes a specific file from the drive.

        Args:
            remote_file_path: Full path to the file (e.g. 'General/Old/report.pdf').

        Returns:
            True if deleted successfully.

        Raises:
            FileNotFoundError: If file does not exist.
            OneDriveIntegrationError: If deletion fails due to API/Permission errors.
        """
        try:
            path_parts = remote_file_path.strip("/").split("/")
            file_name = path_parts[-1]
            folder_path = "/".join(path_parts[:-1])

            parent_folder = self._navigate_folder(folder_path, create_missing=False)
            
            target_file = None
            for item in parent_folder.get_items():
                if item.is_file and item.name == file_name:
                    target_file = item
                    break
            
            if not target_file:
                raise FileNotFoundError(f"File '{file_name}' not found in '{folder_path}'.")

            logger.info(f"Deleting file: {remote_file_path}")
            return target_file.delete()

        except Exception as e:
            logger.error(f"Delete file failed: {e}")
            raise OneDriveIntegrationError(f"Could not delete '{remote_file_path}': {str(e)}") from e

    def delete_folder(self, remote_folder_path: str, allow_non_empty: bool = False) -> bool:
        """Deletes a folder. Safe by default (fails if folder is not empty).

        Args:
            remote_folder_path: Path to the folder (e.g. 'General/OldFiles').
            allow_non_empty: If True, deletes the folder AND all its contents recursively.
                If False (default), raises error if folder has items.

        Returns:
            True if deleted successfully.

        Raises:
            OneDriveIntegrationError: If folder is not empty (and allow_non_empty=False) 
                or if deletion fails.
        """
        try:
            target_folder = self._navigate_folder(remote_folder_path, create_missing=False)
            
            # Safety check: prevent accidental deletion of full folders.
            if not allow_non_empty:
                items = list(target_folder.get_items(limit=1))
                if len(items) > 0:
                    raise OneDriveIntegrationError(
                        f"Folder '{remote_folder_path}' is not empty. "
                        "Set allow_non_empty=True to force delete."
                    )

            logger.warning(f"Deleting folder: {remote_folder_path} (Recursive={allow_non_empty})")
            return target_folder.delete()

        except Exception as e:
            logger.error(f"Delete folder failed: {e}")
            raise OneDriveIntegrationError(f"Could not delete folder '{remote_folder_path}': {str(e)}") from e
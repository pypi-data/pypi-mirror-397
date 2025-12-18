import base64
import os
from email.utils import parseaddr
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests
from msal import ConfidentialClientApplication


class OutlookMailboxClient:
    """Encapsulates Microsoft Graph mailbox interactions for the docscan project."""

    RESOURCE = "https://graph.microsoft.com/"
    API_VERSION = "v1.0"
    SCOPE = ["https://graph.microsoft.com/.default"]

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
        mailbox_email: Optional[str] = None,
        session: Optional[requests.Session] = None,
        debug: bool = False,
    ) -> None:
        self.client_id = client_id or os.getenv("GRAPH_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("GRAPH_CLIENT_SECRET")
        self.tenant_id = tenant_id or os.getenv("GRAPH_TENANT_ID")
        self.mailbox_email = mailbox_email or os.getenv("GRAPH_MAILBOX_EMAIL")
        self.session = session or requests.Session()
        self.debug = debug
        self._authority_url = f"https://login.microsoftonline.com/{self.tenant_id}"

    @property
    def users_endpoint(self) -> str:
        return f"{self.RESOURCE}{self.API_VERSION}/users"

    @property
    def mail_endpoint(self) -> str:
        return f"{self.RESOURCE}{self.API_VERSION}/users/{self.mailbox_email}/messages"

    @property
    def archive_folder_endpoint(self) -> str:
        return f"{self.RESOURCE}{self.API_VERSION}/users/{self.mailbox_email}/mailFolders/Archive"

    def get_access_token(self) -> str:
        app = ConfidentialClientApplication(
            self.client_id,
            authority=self._authority_url,
            client_credential=self.client_secret,
        )
        token_response = app.acquire_token_for_client(self.SCOPE)
        token = token_response.get("access_token")
        if not token:
            raise RuntimeError("Failed to acquire access token for Microsoft Graph.")
        return token

    def get_user_ids(
        self, emails: Iterable[str], token: Optional[str] = None
    ) -> Optional[List[Tuple[str, str]]]:
        token = token or self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        email_filter = " or ".join(
            [f"userPrincipalName eq '{email}'" for email in emails]
        )
        filter_query = f"$filter={email_filter}"
        response = self.session.get(f"{self.users_endpoint}?{filter_query}", headers=headers)
        if response.status_code == 200:
            users = response.json()
            return [
                (user["id"], user["userPrincipalName"]) for user in users.get("value", [])
            ]
        if self.debug:
            print(f"Failed to fetch user ids: {response.status_code} {response.text}")
        return None

    def list_messages(
        self,
        token: Optional[str] = None,
        top: int = 50,
        max_pages: int = 1,
        query_params: Optional[Dict[str, str]] = None,
    ) -> List[Dict]:
        """Fetch messages with optional paging; defaults to more than Graph's 10-item page."""
        token = token or self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        # Required by Graph when using $search
        if query_params and "$search" in query_params:
            headers["ConsistencyLevel"] = "eventual"
        params = {"$top": str(top)} if top else {}
        if query_params:
            params.update(query_params)

        messages: List[Dict] = []
        next_url: Optional[str] = self.mail_endpoint
        page_count = 0

        while next_url and page_count < max_pages:
            response = self.session.get(
                next_url,
                headers=headers,
                params=params if "?" not in next_url else None,
            )
            if response.status_code != 200:
                if self.debug:
                    print(f"Failed to list messages: {response.status_code} {response.text}")
                break

            payload = response.json()
            messages.extend(payload.get("value", []))
            next_url = payload.get("@odata.nextLink")
            params = None  # ensure we don't re-apply params when following nextLink
            page_count += 1

        return messages

    def get_attachments(self, message_id: str, token: Optional[str] = None) -> List[Dict]:
        token = token or self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        endpoint = (
            f"{self.RESOURCE}{self.API_VERSION}/users/"
            f"{self.mailbox_email}/messages/{message_id}/attachments"
        )
        response = self.session.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json().get("value", [])
        if self.debug:
            print(f"Failed to get attachments: {response.status_code} {response.text}")
        return []

    def move_message_to_archive(self, message_id: str, token: Optional[str] = None) -> bool:
        token = token or self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        move_payload = {"destinationId": "archive"}
        response = self.session.post(
            f"{self.mail_endpoint}/{message_id}/move", headers=headers, json=move_payload
        )
        if response.status_code == 201:
            if self.debug:
                print(f"Message {message_id} moved to archive successfully.")
            return True
        if self.debug:
            print(f"Failed to move message: {response.status_code} {response.text}")
        return False

    def save_attachment(self, attachment: Dict, base_directory: Optional[str] = None) -> Optional[str]:
        if attachment.get("@odata.type") != "#microsoft.graph.fileAttachment":
            if self.debug:
                print("Skipping non-file attachment.")
            return None

        content_bytes = attachment.get("contentBytes")
        file_name = attachment.get("name")
        if not content_bytes or not file_name:
            if self.debug:
                print("Attachment missing content or name.")
            return None

        file_data = base64.b64decode(content_bytes)
        target_dir = base_directory or (
            "pdf" if file_name.lower().endswith(".pdf") else "xml"
        )
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, file_name)

        with open(file_path, "wb") as file:
            file.write(file_data)

        if self.debug:
            print(f"Saved attachment: {file_path}")
        return file_path


def _sanitize_message_id(message_id: str) -> str:
    """Geef een bestandssysteemveilige suffix voor een message-id."""
    return "".join(ch for ch in message_id if ch.isalnum() or ch in ("-", "_"))


def _normalize_address(raw: Optional[str]) -> Optional[str]:
    """Haal het e-mailadres op en normaliseer hoofd-/kleine letters."""
    if not raw:
        return None
    _, addr = parseaddr(raw)
    candidate = addr or raw
    return candidate.lower()


def _sender_addresses(message: dict) -> List[str]:
    """Verzamel mogelijke afzenderadressen (from, sender, replyTo)."""
    addresses = set()
    for key in ("from", "sender"):
        addr = _normalize_address(
            message.get(key, {}).get("emailAddress", {}).get("address")
        )
        if addr:
            addresses.add(addr)
    for reply_to in message.get("replyTo") or []:
        addr = _normalize_address(reply_to.get("emailAddress", {}).get("address"))
        if addr:
            addresses.add(addr)
    return list(addresses)


def cleanup_downloaded_files(paths: List[str]) -> None:
    """Verwijder de downloadmap van het verwerkte bericht om de werkruimte schoon te houden."""
    if not paths:
        return
    parent_dir = os.path.dirname(paths[0])
    if os.path.isdir(parent_dir):
        os.removedirs(parent_dir) if not os.listdir(parent_dir) else None
        if os.path.isdir(parent_dir):
            # If removing failed due to nested content, fall back to full removal
            import shutil
            shutil.rmtree(parent_dir)


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


class AttachmentCollector:
    """Helper to fetch and store PDF attachments from an Outlook mailbox client."""

    def __init__(self, client: OutlookMailboxClient):
        self.client = client

    def collect_pdf_attachments(
        self,
        allowed_sender_domain: str,
        download_dir: str,
        token: Optional[str] = None,
        tracker: Optional[Any] = None,
        flow: Optional[str] = None,
        top: int = 50,
        max_pages: int = 5,
    ) -> List[tuple[str, List[str]]]:
        """
        Download PDF-bijlagen van toegestane afzenders en retourneer message-id's met paden.

        - allowed_sender_domain: domeinstring om op te matchen (substring, bijv. '@example.com').
        - download_dir: basisdirectory om bijlagen per bericht in op te slaan.
        - tracker: optioneel object met is_processed(message_id, flow) -> bool.
        - flow: optionele flownaam voor de tracker.
        """
        token = token or self.client.get_access_token()
        _ensure_dir(download_dir)
        messages = self.client.list_messages(
            token=token,
            top=top,
            max_pages=max_pages,
            query_params={
                "$select": "id,from,sender,replyTo,hasAttachments,receivedDateTime",
                "$orderby": "receivedDateTime desc",
            },
        )

        collected: List[tuple[str, List[str]]] = []

        for message in messages:
            message_id = message.get("id")
            if not message_id:
                continue
            if tracker and flow and tracker.is_processed(message_id, flow=flow):
                continue
            if message.get("hasAttachments") is False:
                continue
            addresses = _sender_addresses(message)
            if not any(allowed_sender_domain in addr for addr in addresses):
                continue

            attachments = self.client.get_attachments(message_id, token=token)
            if not attachments:
                continue

            message_dir: Optional[str] = None
            pdf_paths: List[str] = []
            for attachment in attachments:
                file_name = attachment.get("name", "")
                if not file_name.lower().endswith(".pdf"):
                    continue
                if message_dir is None:
                    message_dir = os.path.join(download_dir, _sanitize_message_id(message_id))
                    _ensure_dir(message_dir)
                saved = self.client.save_attachment(
                    attachment, base_directory=message_dir
                )
                if saved and saved.lower().endswith(".pdf"):
                    pdf_paths.append(saved)

            if pdf_paths:
                collected.append((message_id, pdf_paths))

        return collected

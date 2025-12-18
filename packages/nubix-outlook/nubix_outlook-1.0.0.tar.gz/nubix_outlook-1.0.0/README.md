# nubix-outlook

Outlook mailbox client built on Microsoft Graph with helpers for fetching messages and downloading attachments.

## Installation

```bash
pip install nubix-outlook
```

## Configuration

Set environment variables (or pass arguments to the client):

- `GRAPH_CLIENT_ID`
- `GRAPH_CLIENT_SECRET`
- `GRAPH_TENANT_ID`
- `GRAPH_MAILBOX_EMAIL`

## Usage

```python
from nubix_outlook import OutlookMailboxClient, AttachmentCollector

client = OutlookMailboxClient()
collector = AttachmentCollector(client)

attachments = collector.collect_pdf_attachments(
    allowed_sender_domain="@example.com",
    download_dir="downloads",
    top=25,
    max_pages=3,
)

for message_id, files in attachments:
    print(message_id, files)
```

### Direct mailbox actions

- `list_messages(top=50, max_pages=1, query_params=None)` fetches messages with optional paging.
- `get_attachments(message_id)` fetches attachments for a message.
- `move_message_to_archive(message_id)` moves a message to the Archive folder.
- `save_attachment(attachment, base_directory=None)` saves a Graph fileAttachment to disk.

### AttachmentCollector

`AttachmentCollector.collect_pdf_attachments(...)` downloads PDF attachments from senders matching `allowed_sender_domain` into per-message subdirectories under `download_dir`. Returns a list of tuples `(message_id, [pdf_paths])`.

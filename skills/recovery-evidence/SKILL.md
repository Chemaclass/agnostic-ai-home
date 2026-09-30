---
name: recovery-evidence
description: "Rules for proving backups and handling recovery secrets. Use when setting up, auditing, restoring, or claiming a backup works, or when storing encryption passwords, salts, or private keys."
---

# Recovery evidence

- Inspect only what the task needs. Copy necessary recovery secrets directly between private files rather than printing them.
- A backup claim needs a restore of the actual remote object, decrypted away from the machine it protects, with meaningful data and integrity checks. Listing files or restoring the local source dump proves less.
- Keep encryption passwords, salts, referenced private keys, and other required recovery state together in the approved durable destination. A private local copy is useful progress, not proof that password-manager storage is complete.
- Report each claim at the level of evidence gathered: listed, downloaded, decrypted, restored, verified.

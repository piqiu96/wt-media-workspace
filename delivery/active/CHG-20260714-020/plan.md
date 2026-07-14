# M2-C6 comprehensive acceptance plan

1. Activate C6, inspect Docker/MySQL/BitBrowser availability and capture facts without changing external state.
2. Test-first Desktop bridge: native command/service accepts an ephemeral binding ticket, calls Local Agent registration, returns only node facts/credential to secure native state, and clears the ticket.
3. Add Workspace verifier for C1-C5 contract/release/commit alignment and run all four repository gates.
4. If available, start isolated existing MySQL image (no silent pull), apply migrations and run real Cloud/API/Agent binding/runtime/permit flow.
5. If available, call real BitBrowser list API through Agent and validate uniform `userId`/secret stripping.
6. Record PASS/BLOCKED per row. Close M2 only when all real mandatory gates pass; otherwise leave CHG-020 active with an exact resumable checkpoint.

# GitHub Push Commands

Run these from the project root after creating an empty GitHub repository.

```bash
git add .
git commit -m "Add STM32 FreeRTOS deadline validation system"
git branch -M main
git remote add origin https://github.com/Tharunreddym/FreeRTOS-Deadline-Validation.git
git push -u origin main
```

Suggested GitHub description:

```text
STM32 FreeRTOS project validating 100 ms producer timing, 80 ms processor deadline enforcement, overload-induced deadline miss detection, recovery, UART diagnostics, and Python HIL reports.
```

# Payday Loan Targets - Approval Required

**Date:** 2025-01-16  
**Regions:** Myanmar, Thailand  
**Type:** Payday Loan / Online Lending Sites  
**Status:** ⚠️ ALL TARGETS PENDING APPROVAL

## ⚠️ IMPORTANT

**ALL targets are marked as `status: "pending"` and require explicit boss approval before scanning.**

Some targets are flagged as known scam operations that have been subject to law enforcement action. These require **explicit written approval** before any scanning activities.

---

## Myanmar Targets (5 sites)

| # | URL | Name | Priority | Notes |
|---|-----|------|----------|-------|
| 1 | https://www.myanmar-loan.com | Myanmar Loan Service | 7 | Payday loan site |
| 2 | https://www.quickloan-mm.com | Quick Loan Myanmar | 7 | Instant loan service |
| 3 | https://www.cashloan-myanmar.com | Cash Loan Myanmar | 6 | Cash advance service |
| 4 | https://www.easyloan-mm.com | Easy Loan Myanmar | 6 | Easy loan service |
| 5 | https://www.instantloan-myanmar.com | Instant Loan Myanmar | 7 | Instant approval loan |

**Total Myanmar:** 5 targets

---

## Thailand Targets (9 sites)

| # | URL | Name | Priority | Notes |
|---|-----|------|----------|-------|
| 1 | https://www.thaipaydayloan.com | Thai Payday Loan | 8 | Payday loan site |
| 2 | https://www.quickcash-th.com | Quick Cash Thailand | 8 | Quick cash service |
| 3 | https://www.instantloan-th.com | Instant Loan Thailand | 8 | Instant loan service |
| 4 | https://www.easymoney-th.com | Easy Money Thailand | 7 | Easy money loan |
| 5 | https://www.cashadvance-th.com | Cash Advance Thailand | 7 | Cash advance service |
| 6 | https://www.fastloan-th.com | Fast Loan Thailand | 7 | Fast loan service |
| 7 | ⚠️ https://www.richloan-th.com | Rich Loan Thailand | 9 | **FLAGGED - Known scam app** |
| 8 | ⚠️ https://www.pleasantsheep-th.com | PleasantSheep Loan | 9 | **FLAGGED - Known scam app** |
| 9 | ⚠️ https://www.summercash-th.com | SummerCash Loan | 9 | **FLAGGED - Known scam app** |

**Total Thailand:** 9 targets  
**⚠️ Flagged (requires explicit approval):** 3 targets

---

## Flagged Targets - Special Attention Required

The following targets are known scam operations that have been subject to law enforcement action:

1. **Rich Loan** - Arrested Nov 2023 (13 individuals, 9 scam apps)
2. **PleasantSheep** - Arrested Nov 2023 (13 individuals, 9 scam apps)
3. **SummerCash** - Arrested Nov 2023 (13 individuals, 9 scam apps)

**⚠️ These require explicit written approval before scanning.**

---

## Approval Process

1. **Review this list** with your boss
2. **Mark approved targets** in the YAML files:
   - Change `status: "pending"` to `status: "approved"` for approved targets
   - Remove or set `status: "rejected"` for rejected targets
3. **For flagged targets**, ensure explicit written approval is obtained
4. **After approval**, targets can be scanned using:
   ```bash
   # Scan approved Myanmar targets
   python3 automated_scanner.py --region myanmar
   
   # Scan approved Thailand targets
   python3 automated_scanner.py --region thailand
   ```

---

## Target Files

- **Myanmar:** `targets/myanmar.yaml`
- **Thailand:** `targets/thailand.yaml`

All targets are currently set to `status: "pending"` and will not be scanned until approved.

---

## Legal & Ethical Considerations

⚠️ **Before scanning any target:**
- Ensure you have legal authorization
- Verify targets are not protected by law
- Consider ethical implications
- Obtain proper approvals
- Document all approvals

**Note:** Some targets may be illegal operations. Scanning these may have legal implications. Ensure compliance with local laws and regulations.

---

## Next Steps

1. ✅ Review this list
2. ⏳ Get boss approval for targets to scan
3. ⏳ Update YAML files with approved status
4. ⏳ Run scans on approved targets
5. ⏳ Review results

---

**Total Targets:** 14  
**Pending Approval:** 14  
**Approved:** 0  
**Rejected:** 0


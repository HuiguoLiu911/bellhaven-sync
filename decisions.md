# Bellhaven CRM sync: 29 proposals (decisions)

## #53 [chow] CHOW: Bellhaven of Marietta (Cedar Trail Communities (Parent Account) -> Bellhaven)

**Status:** applied (2026-10-13 19:28:57Z) | reviewer note: Approved after review (batch, see review notes in README) | created: 0018D888AB5F96B492

**Reasoning:** Facility is listed on the Bellhaven website but the CRM account sits under Cedar Trail Communities (Parent Account). Revenue history AND outstanding AR > 0 -> billing needs the old account preserved: do NOT re-parent; create a new account under the correct parent and set chow_current_account on the old one.

- **SOP:** revenue $51,250, AR $3,800 -> Revenue history AND outstanding AR > 0 -> billing needs the old account preserved: do NOT re-parent; create a new account under the correct parent and set chow_current_account on the old one.
- **Website:** Bellhaven of Marietta | 805 Colegate Dr, Marietta, OH 45750 | care: Short-Term Rehabilitation & Nursing | admin: Rosa Dietz | phone: (614) 337-1967
- **CRM 001A34WFSUYHCRBLFT:** Bellhaven of Marietta | parent: Cedar Trail Communities (Parent Account) | 805 Colegate Drive, Marietta, OH 45750 | Skilled Nursing | Active | rev $51,250 / AR $3,800 | contacts: -
- **Signals:** [ok] Street matches after normalization ('805 Colegate Drive' ~ '805 Colegate Dr'); [ok] City/state: CRM Marietta, OH vs website Marietta, OH; [ok] ZIP: CRM 45750 vs website 45750; [info] Phone: CRM (419) 353-5019 vs website (614) 337-1967; [info] Website administrator 'Rosa Dietz' is not a contact on this account; [ok] Name similarity 1.00: 'Bellhaven of Marietta' vs 'Bellhaven of Marietta'

**Writes on approval:**

- `create` NEW ACCOUNT . `name`: Bellhaven of Marietta
- `create` NEW ACCOUNT . `parent_id`: 0015QAPLGS3FVYEEEM (Bellhaven Senior Living (Parent Account))
- `create` NEW ACCOUNT . `billing_street`: 805 Colegate Dr
- `create` NEW ACCOUNT . `billing_city`: Marietta
- `create` NEW ACCOUNT . `billing_state`: OH
- `create` NEW ACCOUNT . `billing_zip`: 45750
- `create` NEW ACCOUNT . `care_type`: Skilled Nursing
- `create` NEW ACCOUNT . `phone`: (614) 337-1967
- `create` NEW ACCOUNT . `status`: Active
- `create` NEW ACCOUNT . `note`: [2026-10-13 bellhaven-sync] CHOW successor of 001A34WFSUYHCRBLFT (Bellhaven of Marietta, previously under Cedar Trail Communities (Parent Account)). Old account preserved for billing per SOP.
- `update` 001A34WFSUYHCRBLFT . `chow_current_account`:  -> (id of new account)

## #56 [chow] CHOW: Bellhaven of Tiffin (Cedar Trail Communities (Parent Account) -> Bellhaven)

**Status:** applied (2026-10-13 19:28:58Z) | reviewer note: Approved after review (batch, see review notes in README) | created: 0016FC3097DA2800E7

**Reasoning:** Facility is listed on the Bellhaven website but the CRM account sits under Cedar Trail Communities (Parent Account). Revenue history AND outstanding AR > 0 -> billing needs the old account preserved: do NOT re-parent; create a new account under the correct parent and set chow_current_account on the old one.

- **SOP:** revenue $84,000, AR $12,400 -> Revenue history AND outstanding AR > 0 -> billing needs the old account preserved: do NOT re-parent; create a new account under the correct parent and set chow_current_account on the old one.
- **Website:** Bellhaven of Tiffin | 45 St Lawrence Dr, Tiffin, OH 44883 | care: Short-Term Rehabilitation & Nursing | admin: Walt Osei | phone: (260) 589-2589
- **CRM 001U6RW32TY0WSXZZB:** Bellhaven of Tiffin | parent: Cedar Trail Communities (Parent Account) | 45 St Lawrence Dr, Tiffin, OH 44883 | Skilled Nursing | Active | rev $84,000 / AR $12,400 | contacts: -
- **Signals:** [ok] Street matches after normalization ('45 St Lawrence Dr' ~ '45 St Lawrence Dr'); [ok] City/state: CRM Tiffin, OH vs website Tiffin, OH; [ok] ZIP: CRM 44883 vs website 44883; [info] Phone: CRM (614) 829-9278 vs website (260) 589-2589; [info] Website administrator 'Walt Osei' is not a contact on this account; [ok] Name similarity 1.00: 'Bellhaven of Tiffin' vs 'Bellhaven of Tiffin'

**Writes on approval:**

- `create` NEW ACCOUNT . `name`: Bellhaven of Tiffin
- `create` NEW ACCOUNT . `parent_id`: 0015QAPLGS3FVYEEEM (Bellhaven Senior Living (Parent Account))
- `create` NEW ACCOUNT . `billing_street`: 45 St Lawrence Dr
- `create` NEW ACCOUNT . `billing_city`: Tiffin
- `create` NEW ACCOUNT . `billing_state`: OH
- `create` NEW ACCOUNT . `billing_zip`: 44883
- `create` NEW ACCOUNT . `care_type`: Skilled Nursing
- `create` NEW ACCOUNT . `phone`: (260) 589-2589
- `create` NEW ACCOUNT . `status`: Active
- `create` NEW ACCOUNT . `note`: [2026-10-13 bellhaven-sync] CHOW successor of 001U6RW32TY0WSXZZB (Bellhaven of Tiffin, previously under Cedar Trail Communities (Parent Account)). Old account preserved for billing per SOP.
- `update` 001U6RW32TY0WSXZZB . `chow_current_account`:  -> (id of new account)

## #59 [stale_chow] CHOW: Bellhaven of Sandusky now owned by Millstone Health Partners (Parent Account)

**Status:** applied (2026-10-13 19:29:04Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** No longer on the Bellhaven website, and Millstone Health Partners (Parent Account) already has an account (Millstone Care of Sandusky) at the same address, so the facility changed ownership. Revenue history AND outstanding AR > 0 -> billing needs the old account preserved: do NOT re-parent; create a new account under the correct parent and set chow_current_account on the old one. The current-owner account already exists, so we link to it instead of creating a second copy.

- Not found among 35 communities scraped from the Bellhaven website (directory pages + homepage) on 2026-10-13.
- **SOP:** revenue $130,000, AR $5,200 -> Revenue history AND outstanding AR > 0 -> billing needs the old account preserved: do NOT re-parent; create a new account under the correct parent and set chow_current_account on the old one.
- **CRM 001SXSF4ELF0Z2LGDM:** Bellhaven of Sandusky | parent: Bellhaven Senior Living (Parent Account) | 2715 Columbus Ave, Sandusky, OH 44870 | Skilled Nursing | Active | rev $130,000 / AR $5,200 | contacts: Frank Dietz (Director of Nursing)
- **CRM 0017JP8Z1UQ763BVK3:** Millstone Care of Sandusky | parent: Millstone Health Partners (Parent Account) | 2715 Columbus Ave, Sandusky, OH 44870 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: -

**Writes on approval:**

- `update` 001SXSF4ELF0Z2LGDM . `chow_current_account`:  -> 0017JP8Z1UQ763BVK3 (Millstone Care of Sandusky)

## #46 [reparent] Re-parent Bellhaven Crossings of Lima: Harborview Care Group (Parent Account) -> Bellhaven

**Status:** applied (2026-10-13 19:28:58Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Listed on the Bellhaven website but parented to Harborview Care Group (Parent Account). No outstanding AR -> SOP allows re-parenting the existing account directly.

- **SOP:** revenue $47,000, AR $0 -> No outstanding AR -> SOP allows re-parenting the existing account directly.
- **Website:** Bellhaven Crossings of Lima | 3115 N Cole St, Lima, OH 45801 | care: Assisted Living | admin: Tricia Fitch | phone: (231) 539-3617
- **CRM 001LGFPBJY4N9MB6KL:** Bellhaven Crossings of Lima | parent: Harborview Care Group (Parent Account) | 3115 N Cole St, Lima, OH 45801 | Assisted Living | Active | rev $47,000 / AR $0 | contacts: Nadia Sandoval (Administrator)
- **Signals:** [ok] Street matches after normalization ('3115 N Cole St' ~ '3115 N Cole St'); [ok] City/state: CRM Lima, OH vs website Lima, OH; [ok] ZIP: CRM 45801 vs website 45801; [info] Phone: CRM (734) 872-9575 vs website (231) 539-3617; [info] Website administrator 'Tricia Fitch' is not a contact on this account; [ok] Name similarity 1.00: 'Bellhaven Crossings of Lima' vs 'Bellhaven Crossings of Lima'

**Writes on approval:**

- `update` 001LGFPBJY4N9MB6KL . `parent_id`: 001FJZYHR7MLFMNPLL (Harborview Care Group (Parent Account)) -> 0015QAPLGS3FVYEEEM (Bellhaven Senior Living (Parent Account))
- `update` 001LGFPBJY4N9MB6KL . `note`: [2026-10-13 bellhaven-sync] Re-parented from Harborview Care Group (Parent Account) to Bellhaven (https://analyst-assessment-production.up.railway.app/communities/bellhaven-crossings-of-lima).

## #49 [reparent] Re-parent Bellhaven Meadows of Findlay: (no parent) -> Bellhaven

**Status:** applied (2026-10-13 19:28:58Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Listed on the Bellhaven website but parented to (no parent). No outstanding AR -> SOP allows re-parenting the existing account directly.

- **SOP:** revenue $22,000, AR $0 -> No outstanding AR -> SOP allows re-parenting the existing account directly.
- **Website:** Bellhaven Meadows of Findlay | 1800 N Blanchard St, Findlay, OH 45840 | care: Assisted Living, Memory Support | admin: Sam Pruitt | phone: (231) 533-2969
- **CRM 001UKEFGADQ8YCZ4YM:** Bellhaven Meadows of Findlay | parent: (none) | 1800 N Blanchard St, Findlay, OH 45840 | Assisted Living | Active | rev $22,000 / AR $0 | contacts: Sam Pruitt (Administrator)
- **Signals:** [ok] Street matches after normalization ('1800 N Blanchard St' ~ '1800 N Blanchard St'); [ok] City/state: CRM Findlay, OH vs website Findlay, OH; [ok] ZIP: CRM 45840 vs website 45840; [info] Phone: CRM (330) 975-2492 vs website (231) 533-2969; [ok] Website administrator 'Sam Pruitt' is an active contact on this account; [ok] Name similarity 1.00: 'Bellhaven Meadows of Findlay' vs 'Bellhaven Meadows of Findlay'

**Writes on approval:**

- `update` 001UKEFGADQ8YCZ4YM . `parent_id`:  -> 0015QAPLGS3FVYEEEM (Bellhaven Senior Living (Parent Account))
- `update` 001UKEFGADQ8YCZ4YM . `note`: [2026-10-13 bellhaven-sync] Re-parented from (no parent) to Bellhaven (https://analyst-assessment-production.up.railway.app/communities/bellhaven-meadows-of-findlay).

## #57 [reparent] Re-parent Cedar Trail of Zanesville: Cedar Trail Communities (Parent Account) -> Bellhaven

**Status:** applied (2026-10-13 19:28:59Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Listed on the Bellhaven website but parented to Cedar Trail Communities (Parent Account). No revenue history -> SOP allows re-parenting the existing account directly.

- **SOP:** revenue $0, AR $0 -> No revenue history -> SOP allows re-parenting the existing account directly.
- **Website:** Bellhaven of Zanesville | 2680 Maple Ave, Zanesville, OH 43701 | care: Short-Term Rehabilitation & Nursing | admin: Dale Amato | phone: (814) 599-2533
- **CRM 001H1JMVZWP46D5VUF:** Cedar Trail of Zanesville | parent: Cedar Trail Communities (Parent Account) | 2680 Maple Avenue, Zanesville, OH 43701 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: Dale Amato (Administrator)
- **Signals:** [ok] Street matches after normalization ('2680 Maple Avenue' ~ '2680 Maple Ave'); [ok] City/state: CRM Zanesville, OH vs website Zanesville, OH; [ok] ZIP: CRM 43701 vs website 43701; [info] Phone: CRM (517) 817-8191 vs website (814) 599-2533; [ok] Website administrator 'Dale Amato' is an active contact on this account; [info] Name similarity 0.33: 'Cedar Trail of Zanesville' vs 'Bellhaven of Zanesville'

**Writes on approval:**

- `update` 001H1JMVZWP46D5VUF . `parent_id`: 001FWSQ30SFW6S7604 (Cedar Trail Communities (Parent Account)) -> 0015QAPLGS3FVYEEEM (Bellhaven Senior Living (Parent Account))
- `update` 001H1JMVZWP46D5VUF . `name`: Cedar Trail of Zanesville -> Bellhaven of Zanesville
- `update` 001H1JMVZWP46D5VUF . `note`: [2026-10-13 bellhaven-sync] Re-parented from Cedar Trail Communities (Parent Account) to Bellhaven (https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-zanesville); updated name.

## #50 [reparent] Re-parent Kettering Care Centre: Harborview Care Group (Parent Account) -> Bellhaven

**Status:** applied (2026-10-13 19:28:59Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Listed on the Bellhaven website but parented to Harborview Care Group (Parent Account). No revenue history -> SOP allows re-parenting the existing account directly.

- **SOP:** revenue $0, AR $0 -> No revenue history -> SOP allows re-parenting the existing account directly.
- **Website:** Bellhaven of Kettering | 3313 Wilmington Pike, Kettering, OH 45429 | care: Short-Term Rehabilitation & Nursing | admin: Priya Ashby | phone: (231) 269-5449
- **CRM 001WR41PYNWXCAE2X4:** Kettering Care Centre | parent: Harborview Care Group (Parent Account) | 3313 Wilmington Pike, Kettering, OH 45429 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: -
- Other record for same facility: 001B7XZAA3AFALS9GP Kettering Senior Campus (Cedar Trail Communities (Parent Account))
- Other record for same facility: 0016KTS1UAWBRXS09J Kettering Nursing & Rehabilitation (no parent)
- **Signals:** [ok] Street matches after normalization ('3313 Wilmington Pike' ~ '3313 Wilmington Pike'); [ok] City/state: CRM Kettering, OH vs website Kettering, OH; [ok] ZIP: CRM 45429 vs website 45429; [info] Phone: CRM (419) 600-2603 vs website (231) 269-5449; [info] Website administrator 'Priya Ashby' is not a contact on this account; [ok] Name similarity 1.00: 'Kettering Care Centre' vs 'Bellhaven of Kettering'

**Writes on approval:**

- `update` 001WR41PYNWXCAE2X4 . `parent_id`: 001FJZYHR7MLFMNPLL (Harborview Care Group (Parent Account)) -> 0015QAPLGS3FVYEEEM (Bellhaven Senior Living (Parent Account))
- `update` 001WR41PYNWXCAE2X4 . `name`: Kettering Care Centre -> Bellhaven of Kettering
- `update` 001WR41PYNWXCAE2X4 . `note`: [2026-10-13 bellhaven-sync] Re-parented from Harborview Care Group (Parent Account) to Bellhaven (https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-kettering); updated name.

## #54 [duplicate] Duplicate: Bellhaven of Owosso [Bellhaven Senior Living (Parent Account)] -> Bellhaven of Owosso

**Status:** applied (2026-10-13 19:29:03Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Same facility as surviving record 001EGU7BMJ942ZTRE6 (ranked: active, administrator/phone match, already under Bellhaven, revenue history, contacts, exact address, then account id). No merge in the API, so the losing copy is marked Inactive with duplicate_of_account, and its active contacts are moved to the survivor.

- **Website:** Bellhaven of Owosso | 1120 W Main St, Owosso, MI 48867 | care: Assisted Living | admin: Gloria Lambert | phone: (734) 503-1363
- **CRM 001QU150PM4Z15UA71:** Bellhaven of Owosso | parent: Bellhaven Senior Living (Parent Account) | 1120 West Main Street, Owosso, MI 48867 | Assisted Living | Active | rev $0 / AR $0 | contacts: Tricia Lindqvist (Admissions Director)
- **CRM 001EGU7BMJ942ZTRE6:** Bellhaven of Owosso | parent: Bellhaven Senior Living (Parent Account) | 1120 W Main St, Owosso, MI 48867 | Assisted Living | Active | rev $0 / AR $0 | contacts: Gloria Lambert (Administrator)
- **Signals:** [ok] Street matches after normalization ('1120 West Main Street' ~ '1120 W Main St'); [ok] City/state: CRM Owosso, MI vs website Owosso, MI; [ok] ZIP: CRM 48867 vs website 48867; [info] Phone: CRM (330) 383-5991 vs website (734) 503-1363; [info] Website administrator 'Gloria Lambert' is not a contact on this account; [ok] Name similarity 1.00: 'Bellhaven of Owosso' vs 'Bellhaven of Owosso'

**Writes on approval:**

- `update` 001QU150PM4Z15UA71 . `duplicate_of_account`:  -> 001EGU7BMJ942ZTRE6 (Bellhaven of Owosso)
- `update` 001QU150PM4Z15UA71 . `status`: Active -> Inactive
- `update` 001QU150PM4Z15UA71 . `note`: [2026-10-13 bellhaven-sync] Duplicate of 001EGU7BMJ942ZTRE6 (Bellhaven of Owosso); same facility (1120 W Main St, Owosso).
- `move_contact` 003BT8QV7PS7S0XM0P . `account_id`: 001QU150PM4Z15UA71 (Bellhaven of Owosso) -> 001EGU7BMJ942ZTRE6 (Bellhaven of Owosso)

## #48 [duplicate] Duplicate: Cedar Trail of Monroe [Cedar Trail Communities (Parent Account)] -> Bellhaven Gardens of Monroe

**Status:** applied (2026-10-13 19:29:02Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Same facility as surviving record 001U1750VLVJAGG1S5 (ranked: active, administrator/phone match, already under Bellhaven, revenue history, contacts, exact address, then account id). No merge in the API, so the losing copy is marked Inactive with duplicate_of_account.

- **Website:** Bellhaven Gardens of Monroe | 750 Stewart Rd, Monroe, MI 48162 | care: Assisted Living | admin: Phil Mabry | phone: (814) 412-2218
- **CRM 0011AB44D05WLA9HTX:** Cedar Trail of Monroe | parent: Cedar Trail Communities (Parent Account) | 750 Stewart Road, Monroe, MI 48162 | Assisted Living | Active | rev $0 / AR $0 | contacts: -
- **CRM 001U1750VLVJAGG1S5:** Bellhaven Gardens of Monroe | parent: Bellhaven Senior Living (Parent Account) | 750 Stewart Rd, Monroe, MI 48162 | Assisted Living | Active | rev $0 / AR $0 | contacts: Elaine Vogel (Billing Coordinator)
- **Signals:** [ok] Street matches after normalization ('750 Stewart Road' ~ '750 Stewart Rd'); [ok] City/state: CRM Monroe, MI vs website Monroe, MI; [ok] ZIP: CRM 48162 vs website 48162; [info] Phone: CRM (216) 748-7799 vs website (814) 412-2218; [info] Website administrator 'Phil Mabry' is not a contact on this account; [info] Name similarity 0.25: 'Cedar Trail of Monroe' vs 'Bellhaven Gardens of Monroe'

**Writes on approval:**

- `update` 0011AB44D05WLA9HTX . `duplicate_of_account`:  -> 001U1750VLVJAGG1S5 (Bellhaven Gardens of Monroe)
- `update` 0011AB44D05WLA9HTX . `status`: Active -> Inactive
- `update` 0011AB44D05WLA9HTX . `note`: [2026-10-13 bellhaven-sync] Duplicate of 001U1750VLVJAGG1S5 (Bellhaven Gardens of Monroe); same facility (750 Stewart Rd, Monroe).

## #55 [duplicate] Duplicate: Harborview Nursing & Rehab of Port Clinton [Harborview Care Group (Parent Account)] -> Bellhaven of Port Clinton

**Status:** applied (2026-10-13 19:29:03Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Same facility as surviving record 001UELXDAKFRKB8932 (ranked: active, administrator/phone match, already under Bellhaven, revenue history, contacts, exact address, then account id). No merge in the API, so the losing copy is marked Inactive with duplicate_of_account.

- **Website:** Bellhaven of Port Clinton | 1420 Harbor Point Dr, Port Clinton, OH 43452 | care: Short-Term Rehabilitation & Nursing | admin: Brenda Whitfield | phone: (330) 733-6423
- **CRM 001JD2MWRA74LTSN24:** Harborview Nursing & Rehab of Port Clinton | parent: Harborview Care Group (Parent Account) | 1420 Harbor Point Drive, Port Clinton, OH 43452 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: -
- **CRM 001UELXDAKFRKB8932:** Bellhaven of Port Clinton | parent: Bellhaven Senior Living (Parent Account) | 1420 Harbor Point Dr, Port Clinton, OH 43452 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: Angela McAllister (Director of Nursing), Brenda Whitfield (Administrator)
- **Signals:** [ok] Street matches after normalization ('1420 Harbor Point Drive' ~ '1420 Harbor Point Dr'); [ok] City/state: CRM Port Clinton, OH vs website Port Clinton, OH; [ok] ZIP: CRM 43452 vs website 43452; [info] Phone: CRM (216) 314-1338 vs website (330) 733-6423; [info] Website administrator 'Brenda Whitfield' is not a contact on this account; [ok] Name similarity 0.67: 'Harborview Nursing & Rehab of Port Clinton' vs 'Bellhaven of Port Clinton'

**Writes on approval:**

- `update` 001JD2MWRA74LTSN24 . `duplicate_of_account`:  -> 001UELXDAKFRKB8932 (Bellhaven of Port Clinton)
- `update` 001JD2MWRA74LTSN24 . `status`: Active -> Inactive
- `update` 001JD2MWRA74LTSN24 . `note`: [2026-10-13 bellhaven-sync] Duplicate of 001UELXDAKFRKB8932 (Bellhaven of Port Clinton); same facility (1420 Harbor Point Dr, Port Clinton).

## #58 [duplicate] Duplicate: Harborview Shores of Erie [Harborview Care Group (Parent Account)] -> Bellhaven Shores of Erie

**Status:** applied (2026-10-13 19:29:03Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Same facility as surviving record 001CVBBCSDM7YHN220 (ranked: active, administrator/phone match, already under Bellhaven, revenue history, contacts, exact address, then account id). No merge in the API, so the losing copy is marked Inactive with duplicate_of_account.

- **Website:** Bellhaven Shores of Erie | 4930 W Lake Rd, Erie, PA 16505 | care: Assisted Living, Memory Support | admin: Angela Quinn | phone: (614) 792-9343
- **CRM 001BLYF02K97SZLZHH:** Harborview Shores of Erie | parent: Harborview Care Group (Parent Account) | 4930 West Lake Road, Erie, PA 16505 | Assisted Living | Active | rev $0 / AR $0 | contacts: -
- **CRM 001CVBBCSDM7YHN220:** Bellhaven Shores of Erie | parent: Bellhaven Senior Living (Parent Account) | 4930 W Lake Rd, Erie, PA 16505 | Assisted Living | Active | rev $0 / AR $0 | contacts: Angela Quinn (Administrator)
- **Signals:** [ok] Street matches after normalization ('4930 West Lake Road' ~ '4930 W Lake Rd'); [ok] City/state: CRM Erie, PA vs website Erie, PA; [ok] ZIP: CRM 16505 vs website 16505; [info] Phone: CRM (517) 775-8456 vs website (614) 792-9343; [info] Website administrator 'Angela Quinn' is not a contact on this account; [ok] Name similarity 0.67: 'Harborview Shores of Erie' vs 'Bellhaven Shores of Erie'

**Writes on approval:**

- `update` 001BLYF02K97SZLZHH . `duplicate_of_account`:  -> 001CVBBCSDM7YHN220 (Bellhaven Shores of Erie)
- `update` 001BLYF02K97SZLZHH . `status`: Active -> Inactive
- `update` 001BLYF02K97SZLZHH . `note`: [2026-10-13 bellhaven-sync] Duplicate of 001CVBBCSDM7YHN220 (Bellhaven Shores of Erie); same facility (4930 W Lake Rd, Erie).

## #52 [duplicate] Duplicate: Kettering Nursing & Rehabilitation [(no parent)] -> Kettering Care Centre

**Status:** applied (2026-10-13 19:29:02Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Same facility as surviving record 001WR41PYNWXCAE2X4 (ranked: active, administrator/phone match, already under Bellhaven, revenue history, contacts, exact address, then account id). No merge in the API, so the losing copy is marked Inactive with duplicate_of_account.

- **Website:** Bellhaven of Kettering | 3313 Wilmington Pike, Kettering, OH 45429 | care: Short-Term Rehabilitation & Nursing | admin: Priya Ashby | phone: (231) 269-5449
- **CRM 0016KTS1UAWBRXS09J:** Kettering Nursing & Rehabilitation | parent: (none) | 3313 Wilmington Pike, Kettering, OH 45429 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: -
- **CRM 001WR41PYNWXCAE2X4:** Kettering Care Centre | parent: Harborview Care Group (Parent Account) | 3313 Wilmington Pike, Kettering, OH 45429 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: -
- **Signals:** [ok] Street matches after normalization ('3313 Wilmington Pike' ~ '3313 Wilmington Pike'); [ok] City/state: CRM Kettering, OH vs website Kettering, OH; [ok] ZIP: CRM 45429 vs website 45429; [info] Phone: CRM (216) 345-3441 vs website (231) 269-5449; [info] Website administrator 'Priya Ashby' is not a contact on this account; [ok] Name similarity 1.00: 'Kettering Nursing & Rehabilitation' vs 'Bellhaven of Kettering'

**Writes on approval:**

- `update` 0016KTS1UAWBRXS09J . `duplicate_of_account`:  -> 001WR41PYNWXCAE2X4 (Kettering Care Centre)
- `update` 0016KTS1UAWBRXS09J . `status`: Active -> Inactive
- `update` 0016KTS1UAWBRXS09J . `note`: [2026-10-13 bellhaven-sync] Duplicate of 001WR41PYNWXCAE2X4 (Kettering Care Centre); same facility (3313 Wilmington Pike, Kettering).

## #51 [duplicate] Duplicate: Kettering Senior Campus [Cedar Trail Communities (Parent Account)] -> Kettering Care Centre

**Status:** applied (2026-10-13 19:29:02Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Same facility as surviving record 001WR41PYNWXCAE2X4 (ranked: active, administrator/phone match, already under Bellhaven, revenue history, contacts, exact address, then account id). No merge in the API, so the losing copy is marked Inactive with duplicate_of_account.

- **Website:** Bellhaven of Kettering | 3313 Wilmington Pike, Kettering, OH 45429 | care: Short-Term Rehabilitation & Nursing | admin: Priya Ashby | phone: (231) 269-5449
- **CRM 001B7XZAA3AFALS9GP:** Kettering Senior Campus | parent: Cedar Trail Communities (Parent Account) | 3313 Wilmington Pk, Kettering, OH 45429 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: -
- **CRM 001WR41PYNWXCAE2X4:** Kettering Care Centre | parent: Harborview Care Group (Parent Account) | 3313 Wilmington Pike, Kettering, OH 45429 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: -
- **Signals:** [ok] Street matches after normalization ('3313 Wilmington Pk' ~ '3313 Wilmington Pike'); [ok] City/state: CRM Kettering, OH vs website Kettering, OH; [ok] ZIP: CRM 45429 vs website 45429; [info] Phone: CRM (517) 646-8751 vs website (231) 269-5449; [info] Website administrator 'Priya Ashby' is not a contact on this account; [ok] Name similarity 1.00: 'Kettering Senior Campus' vs 'Bellhaven of Kettering'

**Writes on approval:**

- `update` 001B7XZAA3AFALS9GP . `duplicate_of_account`:  -> 001WR41PYNWXCAE2X4 (Kettering Care Centre)
- `update` 001B7XZAA3AFALS9GP . `status`: Active -> Inactive
- `update` 001B7XZAA3AFALS9GP . `note`: [2026-10-13 bellhaven-sync] Duplicate of 001WR41PYNWXCAE2X4 (Kettering Care Centre); same facility (3313 Wilmington Pike, Kettering).

## #47 [duplicate] Duplicate: Monroe Gardens Care Center [Harborview Care Group (Parent Account)] -> Bellhaven Gardens of Monroe

**Status:** applied (2026-10-13 19:29:01Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Same facility as surviving record 001U1750VLVJAGG1S5 (ranked: active, administrator/phone match, already under Bellhaven, revenue history, contacts, exact address, then account id). No merge in the API, so the losing copy is marked Inactive with duplicate_of_account.

- **Website:** Bellhaven Gardens of Monroe | 750 Stewart Rd, Monroe, MI 48162 | care: Assisted Living | admin: Phil Mabry | phone: (814) 412-2218
- **CRM 00159PL81N38KM4FHM:** Monroe Gardens Care Center | parent: Harborview Care Group (Parent Account) | 750 Stewart Rd, Monroe, MI 48162 | Assisted Living | Active | rev $0 / AR $0 | contacts: -
- **CRM 001U1750VLVJAGG1S5:** Bellhaven Gardens of Monroe | parent: Bellhaven Senior Living (Parent Account) | 750 Stewart Rd, Monroe, MI 48162 | Assisted Living | Active | rev $0 / AR $0 | contacts: Elaine Vogel (Billing Coordinator)
- **Signals:** [ok] Street matches after normalization ('750 Stewart Rd' ~ '750 Stewart Rd'); [ok] City/state: CRM Monroe, MI vs website Monroe, MI; [ok] ZIP: CRM 48162 vs website 48162; [info] Phone: CRM (330) 501-4496 vs website (814) 412-2218; [info] Website administrator 'Phil Mabry' is not a contact on this account; [ok] Name similarity 1.00: 'Monroe Gardens Care Center' vs 'Bellhaven Gardens of Monroe'

**Writes on approval:**

- `update` 00159PL81N38KM4FHM . `duplicate_of_account`:  -> 001U1750VLVJAGG1S5 (Bellhaven Gardens of Monroe)
- `update` 00159PL81N38KM4FHM . `status`: Active -> Inactive
- `update` 00159PL81N38KM4FHM . `note`: [2026-10-13 bellhaven-sync] Duplicate of 001U1750VLVJAGG1S5 (Bellhaven Gardens of Monroe); same facility (750 Stewart Rd, Monroe).

## #1 [create] Create account for Amberly Manor

**Status:** applied (2026-10-13 19:28:56Z) | reviewer note: Approved after review (batch, see review notes in README) | created: 00136B1D36A9894BF5

**Reasoning:** No CRM account matches this location's address, or its city plus phone/administrator. Similar-named accounts were checked and rejected (see near misses).

- **Website:** Amberly Manor | 4390 Darrow Rd, Hudson, OH 44236 | care: Assisted Living | admin: Tom Trent | phone: (330) 228-4392
- **Near miss rejected:** Amberly Manor (Juniper Point Healthcare (Parent Account)) 918 S Nevada Ave, Colorado Springs, CO 80903: Similar name but address/location evidence says it is a different facility

**Writes on approval:**

- `create` NEW ACCOUNT . `name`: Amberly Manor
- `create` NEW ACCOUNT . `parent_id`: 0015QAPLGS3FVYEEEM (Bellhaven Senior Living (Parent Account))
- `create` NEW ACCOUNT . `billing_street`: 4390 Darrow Rd
- `create` NEW ACCOUNT . `billing_city`: Hudson
- `create` NEW ACCOUNT . `billing_state`: OH
- `create` NEW ACCOUNT . `billing_zip`: 44236
- `create` NEW ACCOUNT . `care_type`: Assisted Living
- `create` NEW ACCOUNT . `phone`: (330) 228-4392
- `create` NEW ACCOUNT . `status`: Active
- `create` NEW ACCOUNT . `note`: [2026-10-13 bellhaven-sync] Created from Bellhaven website listing https://analyst-assessment-production.up.railway.app/communities/amberly-manor.

## #3 [create] Create account for Bellhaven at Union Square

**Status:** applied (2026-10-13 19:28:56Z) | reviewer note: Approved after review (batch, see review notes in README) | created: 001F2CE112ABB1BDD3

**Reasoning:** No CRM account matches this location's address, or its city plus phone/administrator. Similar-named accounts were checked and rejected (see near misses).

- **Website:** Bellhaven at Union Square | 118 Union Square Dr, New Albany, OH 43054 | care: Assisted Living | admin: Phil Holloway | phone: (330) 519-9639
- **Near miss rejected:** Union Square Senior Living (Juniper Point Healthcare (Parent Account)) 240 Market St, New Albany, OH 43054: Similar name but address/location evidence says it is a different facility

**Writes on approval:**

- `create` NEW ACCOUNT . `name`: Bellhaven at Union Square
- `create` NEW ACCOUNT . `parent_id`: 0015QAPLGS3FVYEEEM (Bellhaven Senior Living (Parent Account))
- `create` NEW ACCOUNT . `billing_street`: 118 Union Square Dr
- `create` NEW ACCOUNT . `billing_city`: New Albany
- `create` NEW ACCOUNT . `billing_state`: OH
- `create` NEW ACCOUNT . `billing_zip`: 43054
- `create` NEW ACCOUNT . `care_type`: Assisted Living
- `create` NEW ACCOUNT . `phone`: (330) 519-9639
- `create` NEW ACCOUNT . `status`: Active
- `create` NEW ACCOUNT . `note`: [2026-10-13 bellhaven-sync] Created from Bellhaven website listing https://analyst-assessment-production.up.railway.app/communities/bellhaven-at-union-square.

## #12 [create] Create account for Bellhaven of Batavia

**Status:** applied (2026-10-13 19:28:57Z) | reviewer note: Approved after review (batch, see review notes in README) | created: 001FD641620AFBBBC5

**Reasoning:** No CRM account matches this location's address, or its city plus phone/administrator.

- **Website:** Bellhaven of Batavia | 2000 Hospital Dr, Batavia, OH 45103 | care: Short-Term Rehabilitation & Nursing | admin: Elaine Lindqvist | phone: (231) 698-3092

**Writes on approval:**

- `create` NEW ACCOUNT . `name`: Bellhaven of Batavia
- `create` NEW ACCOUNT . `parent_id`: 0015QAPLGS3FVYEEEM (Bellhaven Senior Living (Parent Account))
- `create` NEW ACCOUNT . `billing_street`: 2000 Hospital Dr
- `create` NEW ACCOUNT . `billing_city`: Batavia
- `create` NEW ACCOUNT . `billing_state`: OH
- `create` NEW ACCOUNT . `billing_zip`: 45103
- `create` NEW ACCOUNT . `care_type`: Skilled Nursing
- `create` NEW ACCOUNT . `phone`: (231) 698-3092
- `create` NEW ACCOUNT . `status`: Active
- `create` NEW ACCOUNT . `note`: [2026-10-13 bellhaven-sync] Created from Bellhaven website listing https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-batavia.

## #13 [create] Create account for Bellhaven of Carlisle

**Status:** applied (2026-10-13 19:28:57Z) | reviewer note: Approved after review (batch, see review notes in README) | created: 0015261163AE23E389

**Reasoning:** No CRM account matches this location's address, or its city plus phone/administrator.

- **Website:** Bellhaven of Carlisle | 640 Walnut Bottom Rd, Carlisle, PA 17015 | care: Short-Term Rehabilitation & Nursing | admin: Ken Ashby | phone: (260) 386-7765

**Writes on approval:**

- `create` NEW ACCOUNT . `name`: Bellhaven of Carlisle
- `create` NEW ACCOUNT . `parent_id`: 0015QAPLGS3FVYEEEM (Bellhaven Senior Living (Parent Account))
- `create` NEW ACCOUNT . `billing_street`: 640 Walnut Bottom Rd
- `create` NEW ACCOUNT . `billing_city`: Carlisle
- `create` NEW ACCOUNT . `billing_state`: PA
- `create` NEW ACCOUNT . `billing_zip`: 17015
- `create` NEW ACCOUNT . `care_type`: Skilled Nursing
- `create` NEW ACCOUNT . `phone`: (260) 386-7765
- `create` NEW ACCOUNT . `status`: Active
- `create` NEW ACCOUNT . `note`: [2026-10-13 bellhaven-sync] Created from Bellhaven website listing https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-carlisle.

## #11 [update_fields] Update billing_street on Bellhaven of Ashtabula

**Status:** applied (2026-10-13 19:29:00Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Correct parent already; website shows newer values for: billing_street.

- **Website:** Bellhaven of Ashtabula | 3156 W Prospect Rd, Ashtabula, OH 44004 | care: Short-Term Rehabilitation & Nursing | admin: Ned Green | phone: (260) 440-4975
- **CRM 001NXP9X46CWEPSLSV:** Bellhaven of Ashtabula | parent: Bellhaven Senior Living (Parent Account) | PO Box 517, Ashtabula, OH 44004 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: Marie Bianchi (Director of Nursing), Ned Green (Administrator)
- **Signals:** [warn] CRM street 'PO Box 517' is not a physical address; [ok] City/state: CRM Ashtabula, OH vs website Ashtabula, OH; [ok] ZIP: CRM 44004 vs website 44004; [ok] Phone: CRM (260) 440-4975 vs website (260) 440-4975; [ok] Website administrator 'Ned Green' is an active contact on this account; [ok] Name similarity 1.00: 'Bellhaven of Ashtabula' vs 'Bellhaven of Ashtabula'

**Writes on approval:**

- `update` 001NXP9X46CWEPSLSV . `billing_street`: PO Box 517 -> 3156 W Prospect Rd
- `update` 001NXP9X46CWEPSLSV . `note`: [2026-10-13 bellhaven-sync] Updated billing_street to match https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-ashtabula.

## #31 [update_fields] Update billing_zip on Bellhaven of Portsmouth

**Status:** applied (2026-10-13 19:29:00Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Correct parent already; website shows newer values for: billing_zip.

- **Website:** Bellhaven of Portsmouth | 2222 Gallia St, Portsmouth, OH 45662 | care: Short-Term Rehabilitation & Nursing | admin: Tanya Quinn | phone: (330) 431-2495
- **CRM 001CF3LDWVRGL09P4F:** Bellhaven of Portsmouth | parent: Bellhaven Senior Living (Parent Account) | 2222 Gallia St, Portsmouth, OH 45626 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: Tanya Quinn (Administrator)
- **Signals:** [ok] Street matches after normalization ('2222 Gallia St' ~ '2222 Gallia St'); [ok] City/state: CRM Portsmouth, OH vs website Portsmouth, OH; [warn] ZIP: CRM 45626 vs website 45662; [ok] Phone: CRM (330) 431-2495 vs website (330) 431-2495; [ok] Website administrator 'Tanya Quinn' is an active contact on this account; [ok] Name similarity 1.00: 'Bellhaven of Portsmouth' vs 'Bellhaven of Portsmouth'

**Writes on approval:**

- `update` 001CF3LDWVRGL09P4F . `billing_zip`: 45626 -> 45662
- `update` 001CF3LDWVRGL09P4F . `note`: [2026-10-13 bellhaven-sync] Updated billing_zip to match https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-portsmouth.

## #42 [update_fields] Update name on Arbors at Bellhaven Dayton

**Status:** rejected (2026-10-15 02:22:29Z) | reviewer note: punctuation-only, not worth churning the record

**Reasoning:** Correct parent already; website shows newer values for: name.

- **Website:** The Arbors at Bellhaven - Dayton | 2210 Salem Ave, Dayton, OH 45406 | care: Memory Support | admin: Ray Novak | phone: (260) 254-7592
- **CRM 0010KJFP601YNTZVDA:** Arbors at Bellhaven Dayton | parent: Bellhaven Senior Living (Parent Account) | 2210 Salem Ave, Dayton, OH 45406 | Memory Care | Active | rev $0 / AR $0 | contacts: Dale Novak (Admissions Director), Ray Novak (Administrator)
- **Signals:** [ok] Street matches after normalization ('2210 Salem Ave' ~ '2210 Salem Ave'); [ok] City/state: CRM Dayton, OH vs website Dayton, OH; [ok] ZIP: CRM 45406 vs website 45406; [info] Phone: CRM (216) 659-9837 vs website (260) 254-7592; [ok] Website administrator 'Ray Novak' is an active contact on this account; [ok] Name similarity 1.00: 'Arbors at Bellhaven Dayton' vs 'The Arbors at Bellhaven - Dayton'

**Writes on approval:**

- `update` 0010KJFP601YNTZVDA . `name`: Arbors at Bellhaven Dayton -> The Arbors at Bellhaven - Dayton
- `update` 0010KJFP601YNTZVDA . `note`: [2026-10-13 bellhaven-sync] Updated name to match https://analyst-assessment-production.up.railway.app/communities/the-arbors-at-bellhaven-dayton.

## #9 [update_fields] Update name on Bellhaven Health Care Center of Ashland

**Status:** applied (2026-10-13 19:29:00Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Correct parent already; website shows newer values for: name.

- **Website:** Bellhaven Healthcare Centre of Ashland | 1631 Claremont Ave, Ashland, OH 44805 | care: Short-Term Rehabilitation & Nursing | admin: Carla Okafor | phone: (517) 314-5115
- **CRM 001RJ0D7Z5MAZN5HX5:** Bellhaven Health Care Center of Ashland | parent: Bellhaven Senior Living (Parent Account) | 1631 Claremont Ave, Ashland, OH 44805 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: Carla Okafor (Administrator)
- **Signals:** [ok] Street matches after normalization ('1631 Claremont Ave' ~ '1631 Claremont Ave'); [ok] City/state: CRM Ashland, OH vs website Ashland, OH; [ok] ZIP: CRM 44805 vs website 44805; [info] Phone: CRM (734) 319-7813 vs website (517) 314-5115; [ok] Website administrator 'Carla Okafor' is an active contact on this account; [ok] Name similarity 1.00: 'Bellhaven Health Care Center of Ashland' vs 'Bellhaven Healthcare Centre of Ashland'

**Writes on approval:**

- `update` 001RJ0D7Z5MAZN5HX5 . `name`: Bellhaven Health Care Center of Ashland -> Bellhaven Healthcare Centre of Ashland
- `update` 001RJ0D7Z5MAZN5HX5 . `note`: [2026-10-13 bellhaven-sync] Updated name to match https://analyst-assessment-production.up.railway.app/communities/bellhaven-healthcare-centre-of-ashland.

## #36 [update_fields] Update name on Bellhaven Rehab and Nursing of Grove City

**Status:** applied (2026-10-13 19:29:01Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Correct parent already; website shows newer values for: name.

- **Website:** Bellhaven Rehabilitation & Nursing of Grove City | 3985 Broadway, Grove City, OH 43123 | care: Short-Term Rehabilitation & Nursing | admin: Marie Vogel | phone: (614) 555-7729
- **CRM 001TZCSTBZFM6K5BGN:** Bellhaven Rehab and Nursing of Grove City | parent: Bellhaven Senior Living (Parent Account) | 3985 Broadway, Grove City, OH 43123 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: Janet Krueger (Director of Nursing)
- **Signals:** [ok] Street matches after normalization ('3985 Broadway' ~ '3985 Broadway'); [ok] City/state: CRM Grove City, OH vs website Grove City, OH; [ok] ZIP: CRM 43123 vs website 43123; [ok] Phone: CRM (614) 555-7729 vs website (614) 555-7729; [info] Website administrator 'Marie Vogel' is not a contact on this account; [ok] Name similarity 1.00: 'Bellhaven Rehab and Nursing of Grove City' vs 'Bellhaven Rehabilitation & Nursing of Grove City'

**Writes on approval:**

- `update` 001TZCSTBZFM6K5BGN . `name`: Bellhaven Rehab and Nursing of Grove City -> Bellhaven Rehabilitation & Nursing of Grove City
- `update` 001TZCSTBZFM6K5BGN . `note`: [2026-10-13 bellhaven-sync] Updated name to match https://analyst-assessment-production.up.railway.app/communities/bellhaven-rehabilitation-nursing-of-grove-city.

## #2 [update_fields] Update name on Bellhaven of Sycamore Ridge

**Status:** applied (2026-10-13 19:28:59Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Correct parent already; website shows newer values for: name.

- **Website:** Bellhaven at Sycamore Ridge | 7420 Sycamore Ridge Dr, Miamisburg, OH 45342 | care: Assisted Living | admin: Tom Bloom | phone: (260) 365-6510
- **CRM 00191H7JR16471SZ34:** Bellhaven of Sycamore Ridge | parent: Bellhaven Senior Living (Parent Account) | 7420 Sycamore Ridge Dr, Miamisburg, OH 45342 | Assisted Living | Active | rev $0 / AR $0 | contacts: Ingrid Pruitt (Billing Coordinator), Sofia Castellano (Administrator)
- **Signals:** [ok] Street matches after normalization ('7420 Sycamore Ridge Dr' ~ '7420 Sycamore Ridge Dr'); [ok] City/state: CRM Miamisburg, OH vs website Miamisburg, OH; [ok] ZIP: CRM 45342 vs website 45342; [info] Phone: CRM (419) 982-7764 vs website (260) 365-6510; [info] Website administrator 'Tom Bloom' is not a contact on this account; [ok] Name similarity 1.00: 'Bellhaven of Sycamore Ridge' vs 'Bellhaven at Sycamore Ridge'

**Writes on approval:**

- `update` 00191H7JR16471SZ34 . `name`: Bellhaven of Sycamore Ridge -> Bellhaven at Sycamore Ridge
- `update` 00191H7JR16471SZ34 . `note`: [2026-10-13 bellhaven-sync] Updated name to match https://analyst-assessment-production.up.railway.app/communities/bellhaven-at-sycamore-ridge.

## #15 [update_fields] Update name on Chesterton Senior Commons

**Status:** applied (2026-10-13 19:29:00Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Correct parent already; website shows newer values for: name.

- **Website:** Bellhaven of Chesterton | 1250 NW Franklin Street, Chesterton, IN 46304 | care: Short-Term Rehabilitation & Nursing | admin: Karen Reyes | phone: (216) 551-3978
- **CRM 0013NUZQHQUEZ8DXEG:** Chesterton Senior Commons | parent: Bellhaven Senior Living (Parent Account) | 1250 Northwest Franklin St, Chesterton, IN 46304 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: Karen Reyes (Administrator), Marie Barros (Director of Nursing)
- **Signals:** [ok] Street matches after normalization ('1250 Northwest Franklin St' ~ '1250 NW Franklin Street'); [ok] City/state: CRM Chesterton, IN vs website Chesterton, IN; [ok] ZIP: CRM 46304 vs website 46304; [ok] Phone: CRM (216) 551-3978 vs website (216) 551-3978; [ok] Website administrator 'Karen Reyes' is an active contact on this account; [ok] Name similarity 0.50: 'Chesterton Senior Commons' vs 'Bellhaven of Chesterton'

**Writes on approval:**

- `update` 0013NUZQHQUEZ8DXEG . `name`: Chesterton Senior Commons -> Bellhaven of Chesterton
- `update` 0013NUZQHQUEZ8DXEG . `note`: [2026-10-13 bellhaven-sync] Updated name to match https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-chesterton.

## #14 [update_fields] Update name on Riverbend Manor Care Center

**Status:** applied (2026-10-15 02:22:14Z) | reviewer note: Same address (150 River St, Chagrin Falls) and administrator Dale Mabry is a contact: outdated name.

**Reasoning:** Correct parent already; website shows newer values for: name.

- **Website:** Bellhaven of Chagrin Falls | 150 River St, Chagrin Falls, OH 44022 | care: Assisted Living | admin: Dale Mabry | phone: (231) 283-7448
- **CRM 001RJU1X4NBWC1Q0G7:** Riverbend Manor Care Center | parent: Bellhaven Senior Living (Parent Account) | 150 River St, Chagrin Falls, OH 44022 | Assisted Living | Active | rev $0 / AR $0 | contacts: Dale Mabry (Administrator)
- **Signals:** [ok] Street matches after normalization ('150 River St' ~ '150 River St'); [ok] City/state: CRM Chagrin Falls, OH vs website Chagrin Falls, OH; [ok] ZIP: CRM 44022 vs website 44022; [info] Phone: CRM (517) 457-9548 vs website (231) 283-7448; [ok] Website administrator 'Dale Mabry' is an active contact on this account; [info] Name similarity 0.00: 'Riverbend Manor Care Center' vs 'Bellhaven of Chagrin Falls'

**Writes on approval:**

- `update` 001RJU1X4NBWC1Q0G7 . `name`: Riverbend Manor Care Center -> Bellhaven of Chagrin Falls
- `update` 001RJU1X4NBWC1Q0G7 . `note`: [2026-10-13 bellhaven-sync] Updated name to match https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-chagrin-falls.

## #40 [update_fields] Update name on Sunny Acres Retirement Home

**Status:** applied (2026-10-13 19:29:01Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Correct parent already; website shows newer values for: name.

- **Website:** Bellhaven Willow Creek | 8060 Willow Creek Ln, Portage, MI 49024 | care: Memory Support | admin: Walt Mabry | phone: (419) 394-5494
- **CRM 0017MN2JYAJBDS8WQZ:** Sunny Acres Retirement Home | parent: Bellhaven Senior Living (Parent Account) | 8060 Willow Creek Lane, Portage, MI 49024 | Memory Care | Active | rev $0 / AR $0 | contacts: -
- **Signals:** [ok] Street matches after normalization ('8060 Willow Creek Lane' ~ '8060 Willow Creek Ln'); [ok] City/state: CRM Portage, MI vs website Portage, MI; [ok] ZIP: CRM 49024 vs website 49024; [info] Phone: CRM (216) 898-7925 vs website (419) 394-5494; [info] Website administrator 'Walt Mabry' is not a contact on this account; [info] Name similarity 0.00: 'Sunny Acres Retirement Home' vs 'Bellhaven Willow Creek'

**Writes on approval:**

- `update` 0017MN2JYAJBDS8WQZ . `name`: Sunny Acres Retirement Home -> Bellhaven Willow Creek
- `update` 0017MN2JYAJBDS8WQZ . `note`: [2026-10-13 bellhaven-sync] Updated name to match https://analyst-assessment-production.up.railway.app/communities/bellhaven-willow-creek.

## #43 [stale_review] Bellhaven Care Center of Alliance no longer on Bellhaven website

**Status:** applied (2026-10-13 19:29:04Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Under the Bellhaven parent but not on the website, and no other CRM account at that address points to a new owner. We can't tell whether it was sold, closed or renamed, so flag it for a human instead of guessing a parent.

- Not found among 35 communities scraped from the Bellhaven website (directory pages + homepage) on 2026-10-13.
- **SOP:** revenue $0, AR $0 -> No revenue history -> SOP allows re-parenting the existing account directly.
- **CRM 00116ETS45BL7DTQP7:** Bellhaven Care Center of Alliance | parent: Bellhaven Senior Living (Parent Account) | 1785 Freshley Ave, Alliance, OH 44601 | Skilled Nursing | Active | rev $0 / AR $0 | contacts: -

**Writes on approval:**

- `update` 00116ETS45BL7DTQP7 . `status`: Active -> Needs Review
- `update` 00116ETS45BL7DTQP7 . `note`: [2026-10-13 bellhaven-sync] No longer listed on the Bellhaven website; current owner unknown. Parent left as-is pending research.

## #44 [stale_review] Bellhaven of Coldwater no longer on Bellhaven website

**Status:** applied (2026-10-13 19:29:04Z) | reviewer note: Approved after review (batch, see review notes in README)

**Reasoning:** Under the Bellhaven parent but not on the website, and no other CRM account at that address points to a new owner. We can't tell whether it was sold, closed or renamed, so flag it for a human instead of guessing a parent.

- Not found among 35 communities scraped from the Bellhaven website (directory pages + homepage) on 2026-10-13.
- **SOP:** revenue $0, AR $0 -> No revenue history -> SOP allows re-parenting the existing account directly.
- **CRM 0016PVXH4B25HWR7QE:** Bellhaven of Coldwater | parent: Bellhaven Senior Living (Parent Account) | 90 N Michigan Ave, Coldwater, MI 49036 | Assisted Living | Active | rev $0 / AR $0 | contacts: -

**Writes on approval:**

- `update` 0016PVXH4B25HWR7QE . `status`: Active -> Needs Review
- `update` 0016PVXH4B25HWR7QE . `note`: [2026-10-13 bellhaven-sync] No longer listed on the Bellhaven website; current owner unknown. Parent left as-is pending research.


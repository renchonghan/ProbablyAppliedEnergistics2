# Probably Stolen — 原版物品公开索引

> 由 `tools/build_item_catalog.py` 从本机反编译源码生成。
> **仅含 ID / 类型 / tag / 容量 / 价值，不含本地化名称、描述或反编译代码。**
> 详细名称/描述目录留在本地 `reference/item-catalog-detailed.md`，不提交。

- 实际物品条目：**541**
- 战斗能力/效果（非物品）：**137**
- 未使用/调试条目：**59**
- 仅本地化、未映射到目录：**56**
- 物品目录数：**23**

## 目录统计

| 目录 | 条目数 |
|---|---:|
| MiscItem | 124 |
| Module | 66 |
| FoodItem | 40 |
| GunMod | 31 |
| AmenitiesItem | 30 |
| FurnitureItem | 28 |
| Husbandry | 26 |
| Tool | 24 |
| ContainerItem | 23 |
| MedsItem | 23 |
| NpcCharacterItem | 22 |
| GunsItem | 18 |
| Material | 18 |
| Hydroponic | 15 |
| Perk | 15 |
| ShipSystem | 12 |
| MeleeWeaponItem | 10 |
| Wine | 6 |
| PlayerCharacterItem | 4 |
| ExplosiveItem | 3 |
| ArmorItem | 1 |
| ConstructionItem | 1 |
| Equipment | 1 |

## 液体容器

| ID | 容量 | 标记 | 基础价 |
|---|---:|---|---:|
| `1ml_dropper` | 1mL | dropper、graduated | 120 |
| `5ml_dropper` | 5mL | dropper、graduated | 10 |
| `25ml_cylinder` | 25mL | graduated | 7 |
| `50ml_cylinder` | 50mL | graduated | 10 |
| `100ml_cylinder` | 100mL | graduated | 15 |
| `med_bottle_small_pink` | 150mL | - | 3 |
| `med_bottle_blue` | 250mL | - | 3 |
| `med_bottle_orange` | 250mL | - | 3 |
| `med_bottle_red` | 250mL | - | 3 |
| `med_bottle_violet` | 250mL | - | 3 |
| `mini_bottle` | 250mL | - | 3 |
| `small_bottled_water` | 450mL | - | 4 |
| `bottled_water` | 750mL | - | 5 |
| `large_bottled_water` | 2000mL | - | 9 |
| `water_pitcher` | 3000mL | graduated、filter | 25 |
| `water_jug` | 6000mL | - | 15 |
| `ras_water_tank` | 12000mL | - | 0 |

## 物品索引

| ID | 类型/容量 | 标签 | 价值 |
|---|---|---|---:|
| `aquascan` | HOUSEHOLD_GOOD, WATER_PURIFICATION_SUPPLY | CAN_USE_ON_NON_OWNED_TAG | 200 |
| `box_tampon` | HOUSEHOLD_GOOD, LUXURY_ITEM | - | 100 |
| `gene_scanner` | TOOL | IMPORTANT_TAG, IS_ITEM_TOGGLE_ON_TAG | 500 |
| `hydroreed_filter` | FILTER, HOUSEHOLD_GOOD, WATER_PURIFICATION_SUPPLY | WATER_FILTER | 20 |
| `kotton_fabric` | FILTER, MATERIAL | WATER_FILTER | 65 |
| `lottery_ticket` | - | REPO_ELIGIBLE_OVERRIDE_TAG | 25 |
| `lottery_ticket_old` | - | REPO_ELIGIBLE_OVERRIDE_TAG | 1 |
| `metal_scanner` | TOOL | IMPORTANT_TAG | 250 |
| `neuroactive_perfume` | LUXURY_ITEM | - | 150 |
| `nutrient_tablet` | FARMING_SUPPLIES | NUTRIENT_TABLET | 5 |
| `nutrient_tablet_container` | FARMING_SUPPLIES | CONTAINER_TOOLTIP_TAG, PRE_CONTAINER_TAG | 1 |
| `pack_condom` | HOUSEHOLD_GOOD | - | 35 |
| `packet_red_cigarette` | SUBSTANCE | CIGARETTE_TAG | 80 |
| `paper_towel` | HOUSEHOLD_GOOD | - | 35 |
| `pheromone_perfume` | LUXURY_ITEM | - | 200 |
| `portable_water_purifier` | HOUSEHOLD_GOOD, LUXURY_ITEM, WATER_PURIFICATION_SUPPLY | - | 325 |
| `self_refilling_neuroactive_perfume` | LUXURY_ITEM | IMPORTANT_TAG | 1000 |
| `shampoo` | HOUSEHOLD_GOOD | - | 30 |
| `skincare_cream` | LUXURY_ITEM | - | 500 |
| `toilet_paper` | HOUSEHOLD_GOOD | - | 25 |
| `toothpaste` | HOUSEHOLD_GOOD | - | 15 |
| `uv_filter` | WATER_PURIFICATION_SUPPLY | WATER_FILTER | 150 |
| `water_filter` | FILTER, HOUSEHOLD_GOOD, WATER_PURIFICATION_SUPPLY | WATER_FILTER | 25 |
| `water_filter_adv` | FILTER, HOUSEHOLD_GOOD, LUXURY_ITEM | WATER_FILTER | 350 |
| `water_pitcher` | 3000mL, graduated, filter, HOUSEHOLD_GOOD | CONTAINER_TOOLTIP_TAG | - |
| `water_tablet` | HOUSEHOLD_GOOD, WATER_PURIFICATION_SUPPLY | WATER_PURIFICATION_TABLET | 6 |
| `water_tablet_container` | HOUSEHOLD_GOOD, WATER_PURIFICATION_SUPPLY | CONTAINER_TOOLTIP_TAG, PRE_CONTAINER_TAG | 1 |
| `water_tank` | - | - | - |
| `water_test_container` | HOUSEHOLD_GOOD, WATER_PURIFICATION_SUPPLY | CONTAINER_TOOLTIP_TAG, PRE_CONTAINER_TAG | 1 |
| `water_test_strip` | HOUSEHOLD_GOOD, WATER_PURIFICATION_SUPPLY | CAN_USE_ON_NON_OWNED_TAG, WATER_TESTING_STRIP_TAG | 3 |
| `armor_lining` | - | - | 60 |
| `nuts_metal` | MATERIAL | MATERIAL | 14 |
| `back_inv_save_bag` | - | - | 0 |
| `backpack_large` | - | - | 650 |
| `backpack_large_military` | - | - | 280 |
| `backpack_medium` | - | - | 450 |
| `backpack_medium_military` | - | - | 130 |
| `backpack_small` | - | - | 300 |
| `beerCase` | ALCOHOL, BREVAGE, SUBSTANCE | PRE_CONTAINER_TAG | 1 |
| `eng_box` | - | - | 200 |
| `evidence_box` | - | - | 200 |
| `fanny_pack` | - | backpack, equippable | 50 |
| `hidden_save_bag` | - | - | 0 |
| `kids_backpack` | - | - | 200 |
| `kids_backpack_large` | - | - | 250 |
| `lou_locker` | - | IMPORTANT_TAG, LOU_LOCKER_TAG | - |
| `luxury_supply_crate` | HOUSEHOLD_GOOD, LUXURY_ITEM | IMPORTANT_TAG | 300 |
| `med_box` | - | - | 200 |
| `nutrifruit_seed_packet` | SEED | STORABLE_PACKAGE_TAG | 1 |
| `satchel` | - | backpack, equippable | 150 |
| `save_bag` | - | - | 0 |
| `sec_box` | - | - | 200 |
| `service_box` | - | - | 175 |
| `showcase_save_bag` | - | - | 0 |
| `sold_save_bag` | - | - | 0 |
| `expedition_box` | - | - | 0 |
| `c4_set` | MUNITION, WEAPON | - | 250 |
| `flashbang_grenade` | MUNITION, WEAPON | - | 85 |
| `lou_bomb` | - | IMPORTANT_TAG, LOU_BOMB_ARMED_TAG | 0 |
| `100ml_cylinder` | 100mL, graduated | - | 15 |
| `1ml_dropper` | 1mL, dropper, graduated | - | 120 |
| `25ml_cylinder` | 25mL, graduated | - | 7 |
| `50ml_cylinder` | 50mL, graduated | - | 10 |
| `5ml_dropper` | 5mL, dropper, graduated | - | 10 |
| `beis_icecream` | FOOD, TREAT | - | 40 |
| `bottle_hot_sauce` | FOOD | - | 50 |
| `bottled_water` | 750mL | - | 5 |
| `bottled_water_premium` | LUXURY_ITEM, WATER | - | 325 |
| `cat_bar` | FOOD, TREAT | - | 15 |
| `cup_noodle` | FOOD | - | 20 |
| `empty_beer_bottle` | JUNK | - | 5 |
| `energy_drink` | BREVAGE, TREAT | - | 18 |
| `fat_meat` | FOOD | - | 40 |
| `galaxy_blend` | PROCESSED_FOOD | - | 25 |
| `large_bottled_water` | 2000mL | - | 9 |
| `li_eat_snackbar` | FOOD, TREAT | - | 17 |
| `liquid_luck` | WATER_RATION | LIQUID_LUCK_TAG | 100 |
| `meat_scrap` | - | - | 12 |
| `med_bottle_blue` | 250mL | - | 3 |
| `med_bottle_orange` | 250mL | - | 3 |
| `med_bottle_red` | 250mL | - | 3 |
| `med_bottle_small_pink` | 150mL | - | 1 |
| `med_bottle_violet` | 250mL | - | 3 |
| `mini_bottle` | 250mL | - | 3 |
| `morsel` | FOOD | BIO_PRINTABLE_TAG | 30 |
| `nudka` | ALCOHOL, SUBSTANCE | - | 85 |
| `processed_cheese` | FOOD, PROCESSED_FOOD | - | 20 |
| `processed_juice` | BREVAGE, FOOD, PROCESSED_FOOD | - | 14 |
| `processed_meat` | FOOD, PROCESSED_FOOD | - | 25 |
| `processed_milk` | BREVAGE, FOOD, PROCESSED_FOOD | - | 16 |
| `raw_meat` | FOOD, LUXURY_ITEM | BIO_PRINTABLE_TAG | 159 |
| `red_beer` | ALCOHOL, BREVAGE, SUBSTANCE | RED_IMP_BEER_TAG | 18 |
| `small_bottled_water` | 450mL | - | 4 |
| `small_morsel` | FOOD | BIO_PRINTABLE_TAG | 15 |
| `small_raw_meat` | FOOD | BIO_PRINTABLE_TAG | 65 |
| `soda_red` | BREVAGE, TREAT | - | 15 |
| `water_jug` | 6000mL | - | 15 |
| `water_ration` | WATER_RATION | - | 30 |
| `water_ration_small` | WATER_RATION | - | 15 |
| `blender` | MACHINE | CONTAINER_TAG | 200 |
| `bottle_printer` | - | CONTAINER_TAG, IMPORTANT_TAG | 100 |
| `box_dispenser` | - | IMPORTANT_TAG | 250 |
| `cassette_player` | - | CONTAINER_TOOLTIP_TAG, IMPORTANT_TAG | 0 |
| `chem_finisher` | MACHINE | CONTAINER_TAG | 300 |
| `deal_maker` | MACHINE | STANDARD_MACHINE_TAG | 400 |
| `desequencer` | MACHINE | CONTAINER_TAG, STANDARD_MACHINE_TAG, manufacture | 350 |
| `evaporator` | MACHINE | CONTAINER_TAG, TURBO_BOOST_ELIGIBLE_TAG | 300 |
| `fridge` | MACHINE | CONTAINER_TAG, FRIDGE_TAG, TURBO_BOOST_ELIGIBLE_TAG | 100 |
| `furnace` | - | CONTAINER_TAG, STANDARD_MACHINE_TAG, manufacture | 200 |
| `heating_plate` | MACHINE | CONTAINER_TAG | 250 |
| `hydroponic` | - | CONTAINER_TAG, HYDROPONIC_MACHINE_TAG, STANDARD_MACHINE_TAG, manufacture | 300 |
| `makeshift_reactor` | MACHINE | IMPORTANT_TAG, MAKESHIFT_REACTOR_TAG | 0 |
| `mirage_projector` | MACHINE | IS_PROJECTOR_ACTIVE, STANDARD_MACHINE_TAG | 400 |
| `moisture_farm` | MACHINE | CONTAINER_TAG, STANDARD_MACHINE_TAG, manufacture | 350 |
| `plant_dna_manipulator` | MACHINE | CONTAINER_TAG, DNA_MANIPULATOR_TAG, STANDARD_MACHINE_TAG, manufacture | 1000 |
| `powerblock` | MACHINE | IMPORTANT_TAG | 200 |
| `printer` | - | CONTAINER_TAG, PRINTER_TAG, STANDARD_MACHINE_TAG, manufacture | 350 |
| `recharger` | MACHINE | CONTAINER_TAG, IMPORTANT_TAG, manufacture | 150 |
| `security_alarm` | MACHINE | CONTAINER_TAG, POWERED, STANDARD_MACHINE_TAG, manufacture | 150 |
| `storage_coordinator` | MACHINE | IMPORTANT_TAG, STORAGE_COORDINATOR_TAG | 400 |
| `test_gizmo` | - | - | - |
| `vending_fountain` | - | IMPORTANT_TAG | - |
| `vending_fountain_core` | - | - | - |
| `vending_machine` | - | IMPORTANT_TAG | - |
| `vending_machine_core` | - | - | - |
| `water_purifier` | MACHINE | CONTAINER_TAG, STANDARD_MACHINE_TAG, manufacture | 250 |
| `wine_rack` | MACHINE | CONTAINER_TAG, MACHINE_PERFORMANCE_REDUCES_POWER_TAG, STANDARD_MACHINE_TAG | 350 |
| `ammo_display` | - | - | 70 |
| `barrel` | - | - | 60 |
| `bipod` | - | - | 40 |
| `compensator` | - | - | 50 |
| `gl` | - | - | 150 |
| `grip` | - | - | 40 |
| `grip_gel` | - | - | 70 |
| `internal_springs` | - | - | 40 |
| `internal_springs_improved` | - | - | 20 |
| `laser` | - | - | 50 |
| `laser2` | - | - | 100 |
| `laser_toy` | MAKESHIFT | - | 18 |
| `mag_10mm` | - | - | 30 |
| `mag_10mm_ext` | - | - | 50 |
| `mag_10mm_high` | - | - | 40 |
| `mag_10mm_smg` | - | - | 55 |
| `mag_10mm_smg_box` | - | - | 85 |
| `mag_10mm_smg_high` | - | - | 70 |
| `mag_22` | - | - | 15 |
| `mag_22_ext` | - | - | 35 |
| `mag_22_high` | - | - | 25 |
| `match_barrel` | - | - | 75 |
| `pistol_switch` | - | - | 40 |
| `rds` | - | - | 60 |
| `rds_makeshift` | MAKESHIFT | - | 25 |
| `short_stock` | - | - | 35 |
| `silencer` | - | - | 55 |
| `silencer2` | - | - | 90 |
| `silencer_makeshift` | MAKESHIFT | - | 15 |
| `stock` | - | - | 40 |
| `trigger_group` | - | - | 50 |
| `glock_receiver` | FIREARM, MIDLINE, WEAPON | - | 200 |
| `handmade_pistol` | FIREARM, LOWTECH, WEAPON | - | 120 |
| `handmade_pistol_frame` | - | - | 70 |
| `heavy_handmade_pistol` | FIREARM, LOWTECH, WEAPON | - | 160 |
| `heavy_handmade_pistol_frame` | - | - | 100 |
| `heavy_pistol_ammo` | AMMUNITION | - | 30 |
| `heavy_pistol_ammo_nl` | AMMUNITION | - | 24 |
| `heavy_pistol_ammo_p` | AMMUNITION | - | 36 |
| `lou_etched_round` | - | - | - |
| `printed_gun` | FIREARM, MAKESHIFT, WEAPON | - | 40 |
| `revolver` | FIREARM, MIDLINE, WEAPON | - | 240 |
| `shotgun` | FIREARM, MIDLINE, WEAPON | - | 310 |
| `small_pistol_ammo` | AMMUNITION | - | 20 |
| `small_pistol_ammo_nl` | AMMUNITION | - | 14 |
| `small_pistol_ammo_p` | AMMUNITION | - | 26 |
| `smg` | FIREARM, MIDLINE, WEAPON | - | 280 |
| `stun_gun` | MIDLINE, WEAPON | - | 250 |
| `tazer` | MELEE_WEAPON, WEAPON | - | 100 |
| `animal_cage` | - | CAGE_TAG, CONTAINER_TAG, IMPORTANT_TAG | 250 |
| `auto_butcher` | MACHINE | AUTO_BUTCHER_TAG | 400 |
| `caviar` | - | - | - |
| `eel_fillet` | - | - | - |
| `feces_large` | - | ANIMAL_FECES_TAG | 0 |
| `feces_medium` | - | ANIMAL_FECES_TAG | 0 |
| `feces_small` | - | ANIMAL_FECES_TAG | 0 |
| `fish_fillet` | - | - | - |
| `fish_scrap` | - | - | - |
| `gutterflow_pellet` | - | GUTTERFLOW_PELLET_TAG | - |
| `industrial_fish_feed` | - | INDUSTRIAL_FISH_FEED_TAG | - |
| `large_fish_fillet` | LUXURY_ITEM | - | - |
| `livestock_feed_dispenser` | MACHINE | ALLOWED_IN_CAGE_TAG, FEED_DISPENSER_TAG | 300 |
| `marking_pen` | - | MARKING_PEN_TAG, TOOLBOX_ITEM_TAG | 50 |
| `mouse_trap` | - | CONTAINER_TAG, MOUSE_TRAP_TAG, NESTABLE_DEVICE_TAG | 50 |
| `ras` | - | RAS_FILTER_SLOT_TAG, RAS_TAG, RAS_TANK_GRID_TAG | 300 |
| `ras_water_tank` | 12000mL | IMPORTANT_TAG, RAS_WATER_TANK_TAG | 0 |
| `rat` | - | - | 0 |
| `serum_green` | - | - | 100 |
| `serum_red` | - | - | 100 |
| `small_eel_fillet` | - | - | - |
| `small_fish_fillet` | - | - | - |
| `sturgeon_roe` | - | - | - |
| `tilapia_skin_graft` | MEDICAL | ITEM_MEDICAL_TAG | 24 |
| `tiny_fish_fillet` | - | - | - |
| `vacuum_robot` | - | ALLOWED_IN_CAGE_TAG, IMPORTANT_TAG, VACUUM_INCINERATOR_ON_TAG | 250 |
| `bloomberry_seed` | SEED | - | 40 |
| `coffee_bean` | HOUSEHOLD_GOOD, SEED | - | 28 |
| `dream_cap` | CHEMICAL_SUPPLIES | - | 23 |
| `dream_cap_seed` | SEED | - | 24 |
| `fillerweed` | FOOD | - | 11 |
| `fillerweed_seed` | SEED | - | 9 |
| `hydroreed_seed` | SEED | - | 20 |
| `kotton_fiber` | MATERIAL | - | 46 |
| `kotton_seed` | SEED | - | 20 |
| `meal_cap` | FOOD | - | 19 |
| `nightmare_cap` | CHEMICAL_SUPPLIES, POISON | - | 26 |
| `nutrifruit` | FOOD | - | 12 |
| `nutrifruit_seed` | SEED | - | 40 |
| `plant_analyser` | FARMING_SUPPLIES, TOOL | CAN_USE_ON_NON_OWNED_TAG | 200 |
| `plant_dna_disk` | - | - | 140 |
| `advanced_flux_agent` | MATERIAL | - | 300 |
| `common_chemical` | CHEMICAL_SUPPLIES | - | 50 |
| `common_electronic` | MATERIAL | - | 33 |
| `common_medical` | MEDICAL | - | 40 |
| `common_ore` | BASIC_MATERIAL, MATERIAL | ORE_TAG | 15 |
| `flux_agent` | MATERIAL | - | 4 |
| `gun_part` | MATERIAL | CAN_USE_ON_NON_OWNED_TAG | 25 |
| `hypertech_electronic` | MATERIAL | - | 2500 |
| `junk` | BASIC_MATERIAL, JUNK, MATERIAL | SCRAP_METAL | 3 |
| `metal_ingot` | MATERIAL | - | 50 |
| `nuclear_waste` | - | HAZARDOUS_WASTE_TAG, VENDING_BLACKLISTED_TAG | 0 |
| `printer_plastic` | BASIC_MATERIAL, MATERIAL | PRINTER_MATERIAL_TAG | 12 |
| `rare_electronic` | MATERIAL | - | 350 |
| `rare_ore` | MATERIAL | ORE_TAG | 30 |
| `restricted_chemical` | CHEMICAL_SUPPLIES | - | 100 |
| `restricted_medical` | - | - | - |
| `scrap_metal` | BASIC_MATERIAL, JUNK, MATERIAL | SCRAP_METAL | 10 |
| `wire` | BASIC_MATERIAL, MATERIAL | - | 16 |
| `bandage_item` | MEDICAL | ITEM_MEDICAL_TAG | 8 |
| `black_injector` | LUXURY_ITEM, MEDICAL | - | 350 |
| `blood_bag` | MEDICAL | ITEM_MEDICAL_TAG | 33 |
| `blue_blood_bag` | LUXURY_ITEM, MEDICAL | ITEM_MEDICAL_TAG | 250 |
| `caffeine_pill` | HOUSEHOLD_GOOD, MEDICAL | - | 10 |
| `chem_scanner` | - | CAN_USE_ON_NON_OWNED_TAG | 400 |
| `dream_dust` | MEDICAL, NARCOTIC, SUBSTANCE | - | 18 |
| `fanta_pill` | MEDICAL, NARCOTIC, SUBSTANCE | - | 12 |
| `hemostatic_bandage_item` | MEDICAL | ITEM_MEDICAL_TAG | 16 |
| `large_purple_injector` | MEDICAL | - | 160 |
| `nightmare_dust` | POISON | - | 36 |
| `phagimycin_pill` | - | - | 25 |
| `pink_alt_injector` | - | - | - |
| `pink_injector` | - | - | - |
| `pure_white_injector` | - | - | - |
| `rubbing_alcohol` | MEDICAL | - | 35 |
| `salve` | MEDICAL | - | 80 |
| `smelling_salt` | MEDICAL | ITEM_MEDICAL_TAG | 15 |
| `surgery_tool` | MEDICAL, MEDICAL_TOOL | - | 200 |
| `topical_bandage_item` | MEDICAL | ITEM_MEDICAL_TAG | 16 |
| `unlicensed_phagimycin_pill` | MEDICAL | - | 5 |
| `zerochew` | FOOD, HOUSEHOLD_GOOD | - | 8 |
| `zyanide_pill` | POISON | - | 33 |
| `box_cutter` | HOUSEHOLD_GOOD, MELEE_WEAPON, TOOL | - | 28 |
| `combat_knife` | MELEE_WEAPON, WEAPON | - | 75 |
| `combat_machete` | MELEE_WEAPON, WEAPON | - | 185 |
| `crowbar` | MELEE_WEAPON, TOOL, WEAPON | - | 75 |
| `glass_shard_shiv` | JUNK, MAKESHIFT, MELEE_WEAPON | - | 8 |
| `hatchet` | MELEE_WEAPON, TOOL, WEAPON | - | 55 |
| `kitchen_cleaver` | HOUSEHOLD_GOOD, MELEE_WEAPON, WEAPON | - | 65 |
| `kitchen_knife` | HOUSEHOLD_GOOD, MELEE_WEAPON, WEAPON | - | 45 |
| `pipe_weapon` | JUNK, MAKESHIFT, MELEE_WEAPON | - | 15 |
| `skinning_knife` | MELEE_WEAPON, WEAPON | BUTCHER_TALLY_TAG | 100 |
| `aug_chip` | - | - | 0 |
| `aug_id_guide` | DOCUMENT | DOCUMENT, GUIDE_PAPER_TAG, IMPORTANT_TAG | 50 |
| `aug_scanner` | - | AUG_SCANNER_TAG, CONTAINER_TAG | 200 |
| `black_lamp` | - | IMPORTANT_TAG | 120 |
| `blank_keycard` | ACCESS_CARD | - | 15 |
| `business_permit` | DOCUMENT | DOCUMENT, IMPORTANT_TAG | 0 |
| `canister_mbs` | WEAPON | - | 400 |
| `card_brewer` | DOCUMENT | IMPORTANT_TAG | 0 |
| `card_chem` | DOCUMENT | IMPORTANT_TAG | 0 |
| `card_mining` | DOCUMENT | IMPORTANT_TAG | 0 |
| `card_pharma` | DOCUMENT | IMPORTANT_TAG | 0 |
| `card_rev` | DOCUMENT | IMPORTANT_TAG | 0 |
| `cassette1` | - | - | - |
| `cassette10` | - | - | - |
| `cassette10d` | - | - | - |
| `cassette10l` | - | - | - |
| `cassette11` | - | - | - |
| `cassette11d` | - | - | - |
| `cassette11l` | - | - | - |
| `cassette12` | - | - | - |
| `cassette12d` | - | - | - |
| `cassette12l` | - | - | - |
| `cassette13` | - | - | - |
| `cassette13d` | - | - | - |
| `cassette13l` | - | - | - |
| `cassette14` | - | - | - |
| `cassette14d` | - | - | - |
| `cassette14l` | - | - | - |
| `cassette1d` | - | - | - |
| `cassette1l` | - | - | - |
| `cassette2` | - | - | - |
| `cassette2d` | - | - | - |
| `cassette2l` | - | - | - |
| `cassette3` | - | - | - |
| `cassette3d` | - | - | - |
| `cassette3l` | - | - | - |
| `cassette4` | - | - | - |
| `cassette4d` | - | - | - |
| `cassette4l` | - | - | - |
| `cassette5` | - | - | - |
| `cassette5d` | - | - | - |
| `cassette5l` | - | - | - |
| `cassette6` | - | - | - |
| `cassette6d` | - | - | - |
| `cassette6l` | - | - | - |
| `cassette7` | - | - | - |
| `cassette7d` | - | - | - |
| `cassette7l` | - | - | - |
| `cassette8` | - | - | - |
| `cassette8d` | - | - | - |
| `cassette8l` | - | - | - |
| `cassette9` | - | - | - |
| `cassette9d` | - | - | - |
| `cassette9l` | - | - | - |
| `cert1` | - | - | - |
| `cert2` | - | - | - |
| `cert3` | - | - | - |
| `cert4` | - | - | - |
| `chemistry_guide` | DOCUMENT | DOCUMENT, GUIDE_PAPER_TAG, IMPORTANT_TAG | 50 |
| `cigarette_color` | DOCUMENT | DOCUMENT, IMPORTANT_TAG | 50 |
| `cigarette_guide` | DOCUMENT | DOCUMENT, GUIDE_PAPER_TAG, IMPORTANT_TAG | 50 |
| `cmd_keycard` | ACCESS_CARD | - | 125 |
| `current_converter` | - | IMPORTANT_TAG | 300 |
| `debris_pile1` | - | - | - |
| `debris_pile2` | - | - | - |
| `debris_pile3` | - | - | - |
| `deed` | DOCUMENT | DOCUMENT, IMPORTANT_TAG | 0 |
| `dossier` | - | IMPORTANT_TAG | 0 |
| `drain` | - | IMPORTANT_TAG | 0 |
| `energy_credit` | - | - | - |
| `energy_credit_breeder` | - | - | - |
| `energy_credit_dis` | - | - | - |
| `energy_credit_ext` | - | - | - |
| `energy_credit_hyp` | - | - | 2500 |
| `eng_keycard` | ACCESS_CARD | - | 75 |
| `exchange_directive` | DOCUMENT | IMPORTANT_TAG | 0 |
| `expedition_log` | DOCUMENT | IMPORTANT_TAG | 0 |
| `faucet` | - | IMPORTANT_TAG, IS_TOOLTIP_DISABLED_TAG | 0 |
| `flashlight` | TOOL | - | 40 |
| `food_stamp` | - | - | 30 |
| `fuel_guide` | DOCUMENT | DOCUMENT, GUIDE_PAPER_TAG, IMPORTANT_TAG | 50 |
| `gamblers_coin` | - | GAMBLERS_COIN_TAG, IMPORTANT_TAG | 50 |
| `glass_shard` | JUNK | - | 2 |
| `hand` | - | - | 100 |
| `hand_guide` | DOCUMENT | DOCUMENT, GUIDE_PAPER_TAG, IMPORTANT_TAG | 50 |
| `handnote` | DOCUMENT | IMPORTANT_TAG | 0 |
| `hydroponic_guide` | DOCUMENT | DOCUMENT, GUIDE_PAPER_TAG, IMPORTANT_TAG | 25 |
| `ingot_book` | DOCUMENT | IMPORTANT_TAG | 25 |
| `injector_guide` | DOCUMENT | DOCUMENT, GUIDE_PAPER_TAG, IMPORTANT_TAG | 50 |
| `intel_sec` | DOCUMENT | IMPORTANT_TAG | 0 |
| `joe_card` | DOCUMENT | IMPORTANT_TAG | 0 |
| `logo_checker` | DOCUMENT | DOCUMENT, GUIDE_PAPER_TAG, IMPORTANT_TAG | 50 |
| `lottery_info` | DOCUMENT | DOCUMENT, GUIDE_PAPER_TAG, IMPORTANT_TAG | 1 |
| `lou_old_orders` | DOCUMENT | - | 0 |
| `med_keycard` | ACCESS_CARD | - | 75 |
| `mentor_contract` | DOCUMENT | DOCUMENT, IMPORTANT_TAG | 0 |
| `newspaper` | DOCUMENT | DOCUMENT, IMPORTANT_TAG | 0 |
| `permit_gun_1` | DOCUMENT | IMPORTANT_TAG | 0 |
| `permit_gun_2` | DOCUMENT | IMPORTANT_TAG | 0 |
| `permit_gun_3` | DOCUMENT | IMPORTANT_TAG | 0 |
| `plasma_fuel` | - | - | 300 |
| `plastic_bag` | - | - | 0 |
| `postit` | DOCUMENT | IMPORTANT_TAG | 0 |
| `procurement_slip` | DOCUMENT | DOCUMENT | 0 |
| `republic_transmitter` | - | IMPORTANT_TAG, NOT_FOR_RESALE | 0 |
| `rev_codeword` | - | - | - |
| `ribwich` | - | - | 150 |
| `ribwich_guide` | DOCUMENT | DOCUMENT, GUIDE_PAPER_TAG, IMPORTANT_TAG | 50 |
| `scav_token` | - | IMPORTANT_TAG, SCAV_TOKEN_TAG | 100 |
| `sci_keycard` | ACCESS_CARD | - | 100 |
| `scratcher` | DOCUMENT | - | 20 |
| `scratcher_stack` | DOCUMENT | - | 100 |
| `sec_keycard` | ACCESS_CARD | - | 100 |
| `sec_slip` | DOCUMENT | - | 0 |
| `ser_keycard` | ACCESS_CARD | - | 40 |
| `slip` | DOCUMENT | - | 0 |
| `stamp_guide` | DOCUMENT | DOCUMENT, GUIDE_PAPER_TAG, IMPORTANT_TAG | 50 |
| `sup_keycard` | ACCESS_CARD | - | 40 |
| `trashcan` | - | IMPORTANT_TAG | 0 |
| `tutorial_book` | DOCUMENT | CONTAINER_TAG, DOCUMENT, IMPORTANT_TAG | 0 |
| `tutorial_page` | DOCUMENT | DOCUMENT, IMPORTANT_TAG, TUTORIAL_PAPER_TAG | 0 |
| `wanted_paper` | DOCUMENT | IMPORTANT_TAG | 0 |
| `water_guide` | DOCUMENT | DOCUMENT, GUIDE_PAPER_TAG, IMPORTANT_TAG | 25 |
| `wine_book` | DOCUMENT | DOCUMENT, GUIDE_PAPER_TAG, IMPORTANT_TAG | 25 |
| `alarm_module_transmitter` | MODULE_TYPE_ALARM, ALARM_MODULE | - | 100 |
| `blank_module` | MODULE_TYPE_UNIVERSAL, MODULE | - | 60 |
| `chem_module` | MODULE_TYPE_CHEM, MODULE | - | 250 |
| `crypto_module_cmd` | - | - | 350 |
| `crypto_module_eng` | - | - | 250 |
| `crypto_module_med` | - | - | 250 |
| `crypto_module_sec` | - | - | 300 |
| `crypto_module_ser` | - | - | 200 |
| `crypto_module_sup` | - | - | 200 |
| `dna_manipulator_module_negative_filter` | MODULE_TYPE_DNA_MANIPULATOR | - | 500 |
| `dna_manipulator_module_positive_filter` | MODULE_TYPE_DNA_MANIPULATOR | - | 500 |
| `dna_manipulator_module_precision` | MODULE_TYPE_DNA_MANIPULATOR | - | 1000 |
| `dna_manipulator_module_stabilizer` | MODULE_TYPE_DNA_MANIPULATOR | - | 500 |
| `evaporator_module_solvent_recovery` | MODULE_TYPE_EVAPORATOR, EVAPORATOR_MODULE | - | 275 |
| `farm_module_dream_cap` | MODULE_TYPE_HYDROPONIC, HYDROPONIC_MODULE | - | 150 |
| `farm_module_fillerweed_production` | MODULE_TYPE_HYDROPONIC, HYDROPONIC_MODULE | - | 115 |
| `farm_module_hydroreed_filter` | MODULE_TYPE_HYDROPONIC, HYDROPONIC_MODULE | - | 105 |
| `farm_module_kotton_loom` | MODULE_TYPE_HYDROPONIC, HYDROPONIC_MODULE | - | 200 |
| `farm_module_nightmare_cap` | MODULE_TYPE_HYDROPONIC, HYDROPONIC_MODULE | - | 150 |
| `farm_module_nutrifruit` | MODULE_TYPE_HYDROPONIC, HYDROPONIC_MODULE | - | 150 |
| `farm_module_smuggler` | MODULE_TYPE_HYDROPONIC, HYDROPONIC_MODULE | - | 100 |
| `furnace_module_blast` | MODULE_TYPE_FURNACE, MODULE | - | 150 |
| `furnace_module_junk` | MODULE_TYPE_FURNACE, MODULE | - | 120 |
| `module_bay_expansion_kit` | TOOL | - | 150 |
| `module_extractor` | TOOL | - | 100 |
| `module_extractor_advanced` | TOOL | - | 350 |
| `node_medium` | - | - | 50 |
| `node_small` | - | - | 50 |
| `printer_chip_10_mag` | - | PRINTER_CHIP_TAG | 300 |
| `printer_chip_10_mag_ext` | - | PRINTER_CHIP_TAG | 400 |
| `printer_chip_10_mag_high` | - | PRINTER_CHIP_TAG | 350 |
| `printer_chip_22_mag` | - | PRINTER_CHIP_TAG | 250 |
| `printer_chip_22_mag_ext` | - | PRINTER_CHIP_TAG | 350 |
| `printer_chip_22_mag_high` | - | PRINTER_CHIP_TAG | 300 |
| `printer_chip_box_cutter` | - | PRINTER_CHIP_TAG, PRINTER_MELEE_CHIP_TAG | - |
| `printer_chip_combat_knife` | - | PRINTER_CHIP_TAG, PRINTER_MELEE_CHIP_TAG | - |
| `printer_chip_combat_machete` | - | PRINTER_CHIP_TAG, PRINTER_MELEE_CHIP_TAG | - |
| `printer_chip_gun_part` | - | - | - |
| `printer_chip_handmade_pistol_frame` | - | - | - |
| `printer_chip_hatchet` | - | PRINTER_CHIP_TAG, PRINTER_MELEE_CHIP_TAG | - |
| `printer_chip_heavy_handmade_pistol_frame` | - | - | - |
| `printer_chip_internal_springs_improved` | - | PRINTER_CHIP_TAG | 150 |
| `printer_chip_kitchen_cleaver` | - | PRINTER_CHIP_TAG, PRINTER_MELEE_CHIP_TAG | - |
| `printer_chip_kitchen_knife` | - | PRINTER_CHIP_TAG, PRINTER_MELEE_CHIP_TAG | - |
| `printer_chip_laser_sight` | - | PRINTER_CHIP_TAG | 300 |
| `printer_chip_makeshift_rds` | - | PRINTER_CHIP_TAG | 200 |
| `printer_chip_makeshift_toy_laser` | - | PRINTER_CHIP_TAG | 200 |
| `printer_chip_pistol` | - | PRINTER_CHIP_TAG | 250 |
| `printer_chip_pistol_double` | - | PRINTER_CHIP_TAG | 400 |
| `printer_chip_rds` | - | PRINTER_CHIP_TAG | 300 |
| `printer_chip_silencer` | - | PRINTER_CHIP_TAG | 300 |
| `printer_chip_small_bottle` | - | PRINTER_CHIP_TAG | 100 |
| `printer_module_cnc` | MODULE_TYPE_PRINTER, PRINTER_MODULE | CNC Module | 400 |
| `printer_module_melee_batch` | MODULE_TYPE_PRINTER, PRINTER_MODULE | PRINTER_MELEE_BATCH_MODULE_TAG | 250 |
| `printer_module_metal` | MODULE_TYPE_PRINTER, PRINTER_MODULE | Metal Printing Module | 300 |
| `system_capped_neural_core` | MODULE_TYPE_UNIVERSAL, MODULE | - | 250 |
| `system_module_corrupt` | MODULE_TYPE_UNIVERSAL, MODULE | - | 45 |
| `system_module_eco` | MODULE_TYPE_UNIVERSAL, MODULE | - | 100 |
| `system_module_efficiancy` | MODULE_TYPE_UNIVERSAL, MODULE | - | 70 |
| `system_module_fineness` | MODULE_TYPE_UNIVERSAL, MODULE | - | 100 |
| `system_module_overclock` | MODULE_TYPE_UNIVERSAL, MODULE | - | 100 |
| `system_module_performance` | MODULE_TYPE_UNIVERSAL, MODULE | - | 70 |
| `system_module_quality` | MODULE_TYPE_UNIVERSAL, MODULE | - | 70 |
| `system_module_ruined` | MODULE_TYPE_UNIVERSAL, MODULE | - | 30 |
| `system_module_streamlining` | MODULE_TYPE_UNIVERSAL, MODULE | - | 125 |
| `system_uncapped_neural_core` | MODULE_TYPE_UNIVERSAL, MODULE | - | 1500 |
| `deserter_combat_medic` | - | - | - |
| `deserter_marine` | - | - | - |
| `guard_marine` | - | - | - |
| `merchant` | - | - | - |
| `pirate_chief` | - | - | - |
| `pirate_rookie` | - | - | - |
| `pirate_veteran` | - | - | - |
| `raider_boss` | - | - | - |
| `raider_junker` | - | - | - |
| `raider_marine` | - | - | - |
| `raider_marine_overwatch` | - | - | - |
| `raider_marine_sadistic` | - | - | - |
| `raider_medic` | - | - | - |
| `raider_medic_murderous` | - | - | - |
| `raider_scav` | - | - | - |
| `raider_scav_murderous` | - | - | - |
| `raider_technician` | - | - | - |
| `raider_technician_murderous` | - | - | - |
| `xeno_brewer` | - | - | - |
| `xeno_drone` | - | - | - |
| `xeno_herald` | - | - | - |
| `xeno_hunter` | - | - | - |
| `perk_annoying` | - | - | - |
| `perk_center_mass_acc_buff` | - | - | - |
| `perk_center_mass_cc_debuff` | - | - | - |
| `perk_crafty` | - | - | - |
| `perk_discret` | - | - | - |
| `perk_healthy` | - | - | - |
| `perk_hemophilia` | - | - | - |
| `perk_phagophobia` | - | - | - |
| `perk_pyromaniac` | - | - | - |
| `perk_restorative_metabolism` | - | - | - |
| `perk_sickly` | - | - | - |
| `perk_tenacious` | - | - | - |
| `perk_thrombophilia` | - | - | - |
| `perk_trypanophobia` | - | - | - |
| `perk_venom_adapdation` | - | - | - |
| `albert` | - | - | - |
| `benjamin` | - | - | - |
| `charlotte` | - | - | - |
| `daniel` | - | - | - |
| `hypertech_bay` | STORAGE | SYSTEM_TAG, SYSTEM_TAG_UTILITY | 10000 |
| `machine_bay` | STORAGE | SYSTEM_TAG, SYSTEM_TAG_UTILITY | 300 |
| `machine_bay_ext` | STORAGE | SYSTEM_TAG, SYSTEM_TAG_UTILITY | 1200 |
| `makeshift_storage_bay` | MAKESHIFT, STORAGE | SYSTEM_TAG, SYSTEM_TAG_UTILITY | 250 |
| `smuggler_bay` | STORAGE | CONTAINER_TAG, ITEM_HIDDEN_TAG, SYSTEM_TAG, SYSTEM_TAG_UTILITY | 250 |
| `smuggler_bay_mini` | STORAGE | CONTAINER_TAG, ITEM_HIDDEN_TAG, SYSTEM_TAG, SYSTEM_TAG_UTILITY | 150 |
| `smuggler_bay_mod` | STORAGE | CONTAINER_TAG, ITEM_HIDDEN_TAG, SYSTEM_TAG, SYSTEM_TAG_UTILITY | 400 |
| `storage_bay` | STORAGE | SYSTEM_TAG, SYSTEM_TAG_UTILITY | 300 |
| `storage_bay_chem` | STORAGE | SYSTEM_TAG, SYSTEM_TAG_UTILITY | 400 |
| `storage_bay_expansion_kit` | TOOL | STORAGE_EXPANSION_KIT_TAG | 1063 |
| `storage_bay_gun` | STORAGE | SYSTEM_TAG, SYSTEM_TAG_UTILITY | 400 |
| `storage_bay_large` | STORAGE | SYSTEM_TAG, SYSTEM_TAG_UTILITY | 850 |
| `intake_hopper` | - | HOPPER_INTAKE_TAG | - |
| `labeler` | - | IMPORTANT_TAG, MAGNIFYING_GLASS | 50 |
| `labeler_blue` | - | IMPORTANT_TAG, LABELER_BLUE | 50 |
| `magnifier` | - | CAN_USE_ON_NON_OWNED_TAG, IMPORTANT_TAG, MAGNIFYING_GLASS | 50 |
| `mind_reprogrammer` | TOOL | - | 5000 |
| `outlet_hopper` | - | CONFIGURE_TAG, HOPPER_OUTLET_TAG | - |
| `screwdriver` | TOOL | - | 25 |
| `sign_berry` | - | IMPORTANT_TAG | 100 |
| `sign_expedition` | - | IMPORTANT_TAG | 50 |
| `sign_firearm` | - | IMPORTANT_TAG | 100 |
| `sign_firearm_heavy` | - | IMPORTANT_TAG | 200 |
| `sign_food` | - | IMPORTANT_TAG | 100 |
| `sign_household` | - | IMPORTANT_TAG | 100 |
| `sign_material` | - | IMPORTANT_TAG | 100 |
| `sign_medical` | - | IMPORTANT_TAG | 200 |
| `sign_ruined_machine` | - | IMPORTANT_TAG | 100 |
| `sign_water` | - | IMPORTANT_TAG | 100 |
| `toolbox` | STORAGE | IMPORTANT_TAG | 150 |
| `turbo_booster` | TOOL | - | 35 |
| `turbo_booster_adv` | TOOL | TURBO_BOOST_ADV, TURBO_READY_TAG | 300 |
| `turbo_booster_hypertech` | TOOL | TURBO_BOOST_HYPERTECH | 15000 |
| `welder` | TOOL | - | 80 |
| `wire_cutter` | TOOL | - | 40 |
| `xray_scanner` | TOOL | CAN_USE_ON_NON_OWNED_TAG | 400 |
| `wine_berry` | FOOD | - | 14 |
| `wine_bottle` | - | - | 12 |
| `wine_superyeast` | HOUSEHOLD_GOOD | - | 20 |
| `wine_yeast` | HOUSEHOLD_GOOD | - | 10 |
| `wine_yeast_infinite` | HOUSEHOLD_GOOD | - | 250 |
| `wine_yeast_red` | HOUSEHOLD_GOOD | - | 8 |

## 未使用 / 调试条目（59）

| ID | 类型/容量 | 标签 |
|---|---|---|
| `aloe_vera` | - | - |
| `aloe_vera_gel` | - | ITEM_MEDICAL_TAG |
| `ammo_box` | - | AMMO_BOX_TAG |
| `antique_grenade` | MUNITION, WEAPON | - |
| `armor_titan10` | - | - |
| `armor_titan10h` | - | - |
| `armor_titan10l` | ARMOR | - |
| `armor_titan10s` | - | - |
| `armor_titan9` | - | - |
| `backpack_large_modular` | - | - |
| `backpack_medium_modular` | - | - |
| `backpack_small_modular` | - | - |
| `bicarsole_pill_bottle` | - | ITEM_MEDICAL_TAG |
| `box_nail` | MATERIAL | - |
| `codebook` | DOCUMENT | - |
| `exotic_fuel` | - | EXOTIC_FUEL_TAG |
| `firstaid_box` | - | - |
| `fixalin_pill_bottle` | - | ITEM_MEDICAL_TAG |
| `heavy_handmade_pistol_s` | FIREARM, LOWTECH, WEAPON | - |
| `hemostatic_agent` | - | ITEM_MEDICAL_TAG |
| `inspection_book` | DOCUMENT | CONTAINER_TAG, DOCUMENT, IMPORTANT_TAG |
| `large_storage_bay` | - | SYSTEM_TAG_UTILITY |
| `loan_contract` | DOCUMENT | DOCUMENT, IMPORTANT_TAG |
| `lockpicks` | - | - |
| `lootbox_large` | - | - |
| `lootbox_medium` | - | - |
| `lootbox_small` | - | - |
| `mirage_generator` | - | - |
| `molotov_cocktail` | - | - |
| `ocutol_pill_bottle` | - | ITEM_MEDICAL_TAG |
| `organ_heart` | ORGAN | - |
| `organ_kidney` | - | - |
| `organ_liver` | - | - |
| `organ_lung` | - | - |
| `organ_transport_container` | - | IS_ORGAN_STORE_IN_TRANSPORT_CONTAINER, ORGAN_TRANSPORT_CONTAINER_TAG |
| `oxycodone_pill_bottle` | - | ITEM_MEDICAL_TAG |
| `phagimycin_pill_bottle` | - | ITEM_MEDICAL_TAG |
| `pill_bottle` | - | ITEM_MEDICAL_TAG |
| `pouch_general` | - | - |
| `pouch_general_large` | - | - |
| `pouch_hydration` | - | - |
| `pouch_injector` | - | - |
| `pouch_injector_large` | - | - |
| `pouch_injector_large_double` | - | - |
| `pouch_medical` | - | - |
| `revolver_long` | FIREARM, WEAPON | - |
| `revolver_short` | FIREARM, WEAPON | - |
| `revolver_short_tac` | FIREARM, MIDLINE, WEAPON | - |
| `safe` | - | SAFE_TAG |
| `sec_card` | DOCUMENT | IMPORTANT_TAG |
| `spectral_analyser` | TOOL | - |
| `steel_sheet` | - | - |
| `technician_backpack` | - | backpack, equippable |
| `test_water` | - | - |
| `test_water2` | - | - |
| `test_water3` | - | - |
| `trash_pile` | - | CONTAINER_TAG, IMPORTANT_TAG, PILE_SEARCHED_TODAY |
| `unlicensed_phagimycin_pill_bottle` | - | ITEM_MEDICAL_TAG |
| `wrench_orange` | MELEE_WEAPON, TOOL, WEAPON | - |

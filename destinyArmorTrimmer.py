import csv
import sys
from itertools import permutations 

"""




WARNING! PLEASE READ BEFORE USING: 

This is a harsh script that will tell you to delete a lot of armor.
This script treats all items like they have no masterwork bonus or mods attached, apart from artifice armor.
Artifice armor is treated like 6 different pieces of armor, each with a +3 to each individual stat.

Ultimately, this script just recommends items that you should delete, the actual deleting is up to you.
Review the armor this script has highlighted if you're unsure about the results.




"""


#region "CONFIGURATION"

# Which item rarities in DIM do you want this script to ignore? If an item is marked has a quality defined below, we will ignore the item completely.
# e.g: ['Common', 'Uncommon', 'Rare', 'Legendary', 'Exotic']
config_ignore_rarity = ['Common', 'Uncommon', 'Rare', 'Exotic']

# Which tags in DIM do you want this script to ignore? If an item is marked with a tag listed below, we will ignore the item completely.
# e.g: ['archive', 'infuse', 'junk', 'keep', 'favorite']
config_ignore_tags = ['archive', 'infuse', 'junk']

# Which note hashtags in DIM do you want this script to ignore? If an item has a note with a matching #hashtag, we will ignore the item completely.
# e.g: ['#TRIMIGNORE', '#TESTBUILD']
config_ignore_hashtags = ['#TRIMIGNORE', '#TESTBUILD']

# Which items do you want to include based on their location across all characters and your vault?
# e.g: ['Hunter', 'Titan', 'Warlock', 'Vault']
# This is purely for the location of armor, not the class that can equip it.
# If you include 'Warlock' in this list, it will include all armor currently on your Warlock regardless of if it's actually warlock armor or not.
# You should really check that your destinyArmor.csv file is up to date if you've moved items around before regenerating that file and running this script.
config_only_include_armor_from_location = ['Hunter', 'Titan', 'Warlock', 'Vault']

# Which classes do you want to trim armor for?
# e.g: ['Warlock']
# You can only select one class at a time.
config_only_include_armor_for_class = ['Warlock']

# Should we ignore items that are currently being used in a loadout either in-game or in DIM?
# You would typically want to *not* ignore armor being used in a loadout, so that it can
# be tested with this script and potentially replaced if there's a better item available.
# e.g: True
config_ignore_items_in_loadout = True

# How important are the primary/secondary etc stats on armor?
# This one is a little confusing to explain, but it's basically how strict or forgiving this script will be.
# The default values are the values that I use for sorting my gear.
# Using my default stats, I consider the primary stat I want on armor to be 3 times as important as the 6th stat.
# Consider these multipliers to the base stats of armor. If the script is running a test where
# mobility should be the primary stat on armor, it will increase the base stat of mobility three-fold
# when comparing to the other base stats.
# An armor piece with high mobility will go shooting to the top of the list for best armor pieces,
# while an armor piece with 2 mobility will barely move.

# Modifying these multipliers may result in lots more armor being marked
# for trimming, or potentially a lot less, resulting in less free space
# in your vault. The idea of this script isn't to keep every possible
# combination of armor, but instead to consolidate similar armor pieces
# into one by deleting other pieces.
# !!! It's not really recommended that you touch these values !!!
config_weighted_total_multiplier_first_stat = 3.0 # Default: 3.0
config_weighted_total_multiplier_second_stat = 2.8 # Default: 2.8
config_weighted_total_multiplier_third_stat = 2.0 # Default: 2.0
config_weighted_total_multiplier_fourth_stat = 1.6 # Default: 1.6
config_weighted_total_multiplier_fifth_stat = 1.3 # Default: 1.3
config_weighted_total_multiplier_sixth_stat = 1.0 # Default: 1.0

# --- END OF CONFIGURATION --
#endregion

#region "ERROR HANDLING"

print('\n\n\n\n\n\n\n\n\n\n') # Clear out previous console output to avoid any possible confusion from previous runs of this script

try:
    open('destinyArmor.csv')
except:
    print('ERROR:\nYou need to place your \'destinyArmor.csv\' file in the same location as this script. We could not find this file. If the file is named something different, please rename it to the above.\n\nIn DestinyItemManager, go to \'Organizer\', click on one of your characters to display all their armor, and then click the \'Armor.csv\' button to export a list of all armor across all your characters.\n')
    sys.exit("Error: .csv file not found.")

rawCsvFile = open('destinyArmor.csv', 'r')
csvFile = csv.reader(rawCsvFile)
headers = next(csvFile)
errorHeader = False # I don't believe it's possible to have an destinyArmor.csv file with bad headers generate naturally, but just in case...

if 'Id' not in headers:
    print('There was a problem with the destinyArmor.csv file. Please try regenerating this file in DestinyItemManager.')
    errorHeader = True

if 'Tag' not in headers:
    print('There was a problem with the destinyArmor.csv file. Please try regenerating this file in DestinyItemManager with the tag column visible.')
    errorHeader = True

if 'Equippable' not in headers:
    print('There was a problem with the destinyArmor.csv file. Please try regenerating this file in DestinyItemManager with the equippable character column visible.')
    errorHeader = True

if 'Total (Base)' not in headers:
    print('There was a problem with the destinyArmor.csv file. Please try regenerating this file in DestinyItemManager with the item base stat column visible.')
    errorHeader = True

if 'Notes' not in headers:
    print('There was a problem with the destinyArmor.csv file. Please try regenerating this file in DestinyItemManager with the notes column visible.')
    errorHeader = True
    
if 'Seasonal Mod' not in headers:
    print('There was a problem with the destinyArmor.csv file. Please try regenerating this file in DestinyItemManager with the seasonal mod column visible.')
    errorHeader = True

if 'Tier' not in headers:
    print('There was a problem with the destinyArmor.csv file. Please try regenerating this file in DestinyItemManager with the tier column visible.')
    errorHeader = True

if errorHeader:
    sys.exit("Error: Column data missing in file.")
rawCsvFile.close()

print('destinyArmor.csv read successfully...\nGenerating results...\n')

#endregion

#region "ITEM FILTERING LOGIC"

filteredItems = []
ignoredItems = 0
processedItems = 0                     
with open('destinyArmor.csv', newline='') as csvfile:
    destinyArmorList = csv.DictReader(csvfile)
    for itemRow in destinyArmorList:
        processedItems += 1
        # If the item has no id
        if len(itemRow['Id']) == 0:
            print('... removing item with no id ...')
            ignoredItems += 1
            continue
        # If the item is a rarity that we're ignoring
        if itemRow['Tier'] in config_ignore_rarity:
            print('... removing item with ignored rarity (' + str(itemRow['Tier']) + ') ...')
            ignoredItems += 1
            continue
        # If the item has a DIM tag that we're ignoring
        if itemRow['Tag'] in config_ignore_tags:
            print('... removing item with ignored tag (' + str(itemRow['Tag']) + ') ...')
            ignoredItems += 1
            continue
        # If the item has a DIM note hashtag that we're ignoring
        if any(itemRow['Notes'].find(hashtag) > -1 for hashtag in config_ignore_hashtags):
            print('... removing item with ignored DIM hashtag (' + str(itemRow['Notes']) + ') ...')
            ignoredItems += 1
            continue
        # If the item is not in the specified locations to search for armor
        if not any(itemRow['Owner'].find(location) > -1 for location in config_only_include_armor_from_location):
            print('... removing item not in correct location (' + str(itemRow['Owner']) + ') ...')
            ignoredItems += 1
            continue
        # If the item is not part of the class we're trimming armor for
        if not any(itemRow['Equippable'].find(character) > -1 for character in config_only_include_armor_for_class):
            print('... removing item not for desired class (' + str(itemRow['Equippable']) + ') ...')
            ignoredItems += 1
            continue
        # If the item is in a loadout (and this config option is enabled)
        if config_ignore_items_in_loadout:
            if len(itemRow['Loadouts']) > 0:
                print('... removing item already used in loadout (' + str(itemRow['Loadouts']) + ') ...')
                ignoredItems += 1
                continue
        # If the total base stat is 0 (class items), ignore
        if int(itemRow['Total (Base)']) == 0:
            print('... removing item with no base stats (class item) ...')
            ignoredItems += 1
            continue
        # Add item to chopping block
        itemToAdd = {
            'id': itemRow['Id'].replace('"', ''),
            'name': itemRow['Name'], 
            'tag': itemRow['Tag'], 
            'class': itemRow['Equippable'],
            'stat_base_mobility': int(itemRow['Mobility (Base)']),
            'stat_base_resilience': int(itemRow['Resilience (Base)']),
            'stat_base_recovery': int(itemRow['Recovery (Base)']),
            'stat_base_discipline': int(itemRow['Discipline (Base)']),
            'stat_base_intellect': int(itemRow['Intellect (Base)']),
            'stat_base_strength': int(itemRow['Strength (Base)']),
            'weighted_stat_base_mobility': '',
            'weighted_stat_base_resilience': '',
            'weighted_stat_base_recovery': '',
            'weighted_stat_base_discipline': '',
            'weighted_stat_base_intellect': '',
            'weighted_stat_base_strength': '',
            'weighted_total': '',
            'stat_base_total': int(itemRow['Total (Base)']),
            'seasonal_mod': itemRow['Seasonal Mod'],
            'notes': itemRow['Notes'],
            'loadouts': itemRow['Loadouts'],
            'owner': itemRow['Owner'],
            'type': itemRow['Type'],
            'logic_notes': ''
        }
        if itemToAdd['seasonal_mod'] == 'artifice':
            # mobility
            print('... creating copy of artifice armor with boosted +3 mobility ...')
            mobility_copy = itemToAdd.copy()
            mobility_copy['stat_base_mobility'] += 3
            mobility_copy['logic_notes'] += 'artifice_boost_mobility'
            filteredItems.append(mobility_copy)
            # resilience
            print('... creating copy of artifice armor with boosted +3 resilience ...')
            resilience_copy = itemToAdd.copy()
            resilience_copy['stat_base_resilience'] += 3
            resilience_copy['logic_notes'] += 'artifice_boost_resilience'
            filteredItems.append(resilience_copy)
            # recovery
            print('... creating copy of artifice armor with boosted +3 recovery ...')
            recovery_copy = itemToAdd.copy()
            recovery_copy['stat_base_recovery'] += 3
            recovery_copy['logic_notes'] += 'artifice_boost_recovery'
            filteredItems.append(recovery_copy)
            # discipline
            print('... creating copy of artifice armor with boosted +3 discipline ...')
            discipline_copy = itemToAdd.copy()
            discipline_copy['stat_base_discipline'] += 3
            discipline_copy['logic_notes'] += 'artifice_boost_discipline'
            filteredItems.append(discipline_copy)
            # intellect
            print('... creating copy of artifice armor with boosted +3 intellect ...')
            intellect_copy = itemToAdd.copy()
            intellect_copy['stat_base_intellect'] += 3
            intellect_copy['logic_notes'] += 'artifice_boost_intellect'
            filteredItems.append(intellect_copy)
            # strength
            print('... creating copy of artifice armor with boosted +3 strength ...')
            strength_copy = itemToAdd.copy()
            strength_copy['stat_base_strength'] += 3
            strength_copy['logic_notes'] += 'artifice_boost_strength'
            filteredItems.append(strength_copy)
        else:
            filteredItems.append(itemToAdd)
    print('-- Finished filtering armor')

#endregion

#region "TRIMMING LOGIC"

trimmedItems = []

helmet = []
gauntlets = []
chest_armor = []
leg_armor = []
for item in filteredItems:
    if item['type'] == 'Helmet':
        helmet.append(item)
        continue
    if item['type'] == 'Gauntlets':
        gauntlets.append(item)
        continue
    if item['type'] == 'Chest Armor':
        chest_armor.append(item)
        continue
    if item['type'] == 'Leg Armor':
        leg_armor.append(item)
        continue

print(str(len(helmet)) + ' theoretical helmets')
print(str(len(gauntlets)) + ' theoretical gauntlets')
print(str(len(chest_armor)) + ' theoretical chest_armor')
print(str(len(leg_armor)) + ' theoretical leg_armor')

print('\n>> Running through permutations...')

winning_candidate_ids = []

def FindBestArmor(armorType):
    permutationList = permutations(['stat_base_mobility', 'stat_base_resilience', 'stat_base_recovery', 'stat_base_discipline', 'stat_base_intellect', 'stat_base_strength']) 
    for p in list(permutationList): # For each permutation        

        for item in armorType:
            item['weighted_' + p[0]] = round(item[p[0]] * config_weighted_total_multiplier_first_stat, 2)
            item['weighted_' + p[1]] = round(item[p[1]] * config_weighted_total_multiplier_second_stat, 2)
            item['weighted_' + p[2]] = round(item[p[2]] * config_weighted_total_multiplier_third_stat, 2)
            item['weighted_' + p[3]] = round(item[p[3]] * config_weighted_total_multiplier_fourth_stat, 2)
            item['weighted_' + p[4]] = round(item[p[4]] * config_weighted_total_multiplier_fifth_stat, 2)
            item['weighted_' + p[5]] = round(item[p[5]] * config_weighted_total_multiplier_sixth_stat, 2)
            item['weighted_total'] = round(item['weighted_' + p[0]] + item['weighted_' + p[1]] + item['weighted_' + p[2]] + item['weighted_' + p[3]] + item['weighted_' + p[4]] + item['weighted_' + p[5]], 2)
        
        sorted_list = sorted(armorType, key=lambda x: (-x['weighted_total'])
        )

        #region DEBUG PERMUTATION
        
        if (False):
            if p[0] == 'stat_base_discipline':
                if p[1] == 'stat_base_resilience':
                    if p[2] == 'stat_base_mobility':
                        if p[3] == 'stat_base_strength':
                            if p[4] == 'stat_base_intellect':
                                if p[5] == 'stat_base_recovery':
                                    if sorted_list[0]['type'] == 'Chest Armor':
                                        print('\n------------------------\n\nDEBUG PERMUTATION: \n\n\n')
                                        for item in sorted_list:
                                            if item['id'] == 'XXXXXXXXXXXXXXXXX':
                                                print('v v v v v v')
                                            print('{} : Mob={} Res={} Rec={} Dis={} Int={} Str={} WT={} *={}'.format(
                                                item['id'],
                                                item['stat_base_mobility'],
                                                item['stat_base_resilience'],
                                                item['stat_base_recovery'],
                                                item['stat_base_discipline'],
                                                item['stat_base_intellect'],
                                                item['stat_base_strength'],
                                                item['weighted_total'],
                                                item['logic_notes']
                                            ))
        #endregion

        if sorted_list[0]['id'] not in winning_candidate_ids:
            winning_candidate_ids.append(sorted_list[0]['id'])
            continue

FindBestArmor(helmet)
FindBestArmor(gauntlets)
FindBestArmor(chest_armor)
FindBestArmor(leg_armor)

trimmed_item_ids = []
for item in filteredItems:
    # FIXED: [v1.0.1] - [Only check if item id is a winning candidate, not the whole item] - Artifice armor being deleted if at least one of the six theoretical copies fails a permutation leaderboard test
    if item['id'] not in winning_candidate_ids:
        if item['id'] not in trimmed_item_ids:
            trimmed_item_ids.append(item['id'])
            trimmedItems.append(item)

#endregion

#region "END MESSAGE"

print('\n>> Finished trimming items.')
dimTrimQuery = ''
for ti in trimmedItems:
    #print(str(ti) + '\n')
    dimTrimQuery += 'id:"' + ti["id"] + '" or '

print('\nComplete!\n' + str(len(trimmedItems)) + ' items found to be trimmed.\n-----------------------------\n')
if dimTrimQuery == '':
    print('[ There were no items found in your inventory that needed to be trimmed. ]\n\nIf this doesn\'t seem right, please check your config settings at the top of the script file, or check the destinyArmor.csv file you supplied alongside this script.\n')
else:
    print('Copy and paste the below DIM query into the search bar inside DIM to highlight the items marked for trimming.\nYou can then choose to tag all these items as junk and remove them or just review them.\n\n')
    print(dimTrimQuery.strip(' or ') + '\n')
 

print('Total items: {} | Items ignored: {} | Items evaluated: {} | >> Items to trim: {} <<'.format(str(processedItems), str(ignoredItems) + '/' + str(processedItems), str(processedItems - ignoredItems), str(len(trimmedItems))))

trimmedItemsInLoadouts = 0
for item in trimmedItems:
    if len(item['loadouts']) > 0:
        if trimmedItemsInLoadouts < 1:
            print('\n!!! There are items marked to be trimmed that are being used in existing loadouts !!!\n')
        trimmedItemsInLoadouts += 1
        print('ID: {} ({}) - Loadouts: {}\n'.format(item['id'], item['type'], item['loadouts']))

#endregion

# ---- Changelog ----

# -- [v1.0.1]: --
# > 'Artifice armor permutation fix'
# > FIXED: Only check if item *id* is a winning candidate, not the whole item - (Artifice armor being deleted if at least one of the six theoretical copies fails a permutation leaderboard test)

# -- [v1.0.0]: --
# > NEW: Initial release
        
# --------

#written in a day by @reach
#v1.0.1
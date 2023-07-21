# pcpp contains the C Preprocessor/Evaluator that allows the script to go through includes etc
from pcpp import Preprocessor, Evaluator, OutputDirective, Action
# cxxheaderparser effectively goes through the C file and processes it, allowing the Python script to read it
from cxxheaderparser.simple import parse_file
# os and sys for interaction with the file system
import os
import sys
import re
import shutil

# trusted_typedefs clarifies that the underlying construction doesn't need to be compared (unlike say two instances of a BoxPokemon struct) 
trusted_typedefs = {
    'u8': [0, pow(2, 8) - 1],
    'u16': [0, pow(2, 16) - 1],
    'u32': [0, pow(2, 32) - 1],
    'u64': [0, pow(2, 64) - 1],
    's8': [-(pow(2, 7) - 1), pow(2, 7) - 1],
    's16': [-(pow(2, 15) - 1), pow(2, 15) - 1],
    's32': [-(pow(2, 31) - 1), pow(2, 31) - 1],
    's64': [-(pow(2, 63) - 1), pow(2, 63) - 1],
    'bool8': [0, 1],
    'bool16': [0, 1],
    'bool32': [0, 1],
    'int': [0, 0]
}
# ignoreable includes prevents the preprocessor from complaining about include files that don't exist that we don't need anyway
ignoreable_includes = ['string.h', 'stddef.h', 'stdint.h', 'sprite.h', 'limits.h']
# the following fields are ignored when it comes to migration because they are related to maps and SetContinueGameWarpStatus(); takes care of that
ignored_map_fields = ['weather', 'weatherCycleStage', 'flashLevel', 'savedMusic', 'mapLayoutId', 'mapView', 'objectEvents', 'objectEventTemplates']

globalVersion = 0
globalHasChanges = False
globalDifferences = []

# this class overrides the "include not found" error and prevents it from displaying if it is in ignoreable_includes (i.e. irrelevant)
class PcppPreprocessor(Preprocessor):
    def on_include_not_found(self,is_malformed,is_system_include,curdir,includepath):
        if includepath not in ignoreable_includes:
            if is_malformed:
                self.on_error(self.lastdirective.source,self.lastdirective.lineno, "Malformed #include statement: %s" % includepath)
            else:
                self.on_error(self.lastdirective.source,self.lastdirective.lineno, "Include file '%s' not found" % includepath)
        raise OutputDirective(Action.IgnoreAndPassThrough)

# preprocess a file and store it as files in /versioning with pcpp
def preprocess_files(filename, version):
    p = PcppPreprocessor()
    path = "include/%s.h" % filename
    with open(path, 'rt') as ih:
        p.parse(ih.read(), path)
    with open('versioning/%s_v%s.c' % (filename, version), 'w') as oh:
        p.write(oh)

# pulls global.h and pokemon_storage_system from the source, storing them in a separate versioning folder
def pull_new_version():
    if not os.path.exists("versioning/"):
        os.mkdir("versioning/")
    global globalVersion
    while os.path.exists("versioning/global_v%s.c" % globalVersion):
        globalVersion += 1
    preprocess_files("global", globalVersion)
    preprocess_files("pokemon_storage_system", globalVersion)
    get_sector_id_values(globalVersion)
    if (globalVersion == 0):
        injectTustin()
        quit()

def get_sector_id_values(version):
    with open("include/save.h", 'r') as file:
        rawcode = file.read()
    with open("versioning/sectors_v%s.txt" % version, 'w') as file:
        file.write("%s\n" % fetchDefineValue("SECTOR_ID_SAVEBLOCK2", rawcode))
        file.write("%s\n" % fetchDefineValue("SECTOR_ID_SAVEBLOCK1_START", rawcode))
        file.write("%s\n" % fetchDefineValue("SECTOR_ID_PKMN_STORAGE_START", rawcode))

# injects Tustin's implementation to the game where necessary
def injectTustin():
    out("Saved the current version as v0. Please wait…")
    # add save sentinel to the new saveblock
    with open("include/global.h", 'r') as file:
        content = file.read()
    if not 'u8 _saveSentinel;' in content:
        ncontent = content.replace('struct SaveBlock2\n{\n    ', 'struct SaveBlock2\n{\n    // _saveSentinel and saveVersion are used by the save migration system. Please do not (re)move them.\n    u8 _saveSentinel; // 0xFF\n    // u8 unused;\n    u16 saveVersion;\n    ')
        if ncontent == content: # the injection failed for whatever reason
            failTustinInjection("Unable to inject the necessary data into SaveBlock2! Aborting procedure.")
        with open("include/global.h", 'w') as file:
            file.write(ncontent)
        out("Updated include/global.h")
    # add new game defining
    with open("src/new_game.c", 'r') as file:
        content = file.read()
    if not 'gSaveBlock2Ptr->_saveSentinel = 0xFF;' in content:
        ncontent = content.replace('gSaveBlock2Ptr->encryptionKey = 0;', 'gSaveBlock2Ptr->_saveSentinel = 0xFF;\n    gSaveBlock2Ptr->saveVersion = SAVE_VERSION;\n    gSaveBlock2Ptr->encryptionKey = 0;')
        if ncontent == content: # the injection failed for whatever reason
            failTustinInjection("Unable to inject the necessary data into new_game.c! Aborting procedure.")
        with open("src/new_game.c", 'w') as file:
            file.write(ncontent)
        out("Updated src/new_game.c")
    # uncomment the versioning include in include/constants/global.h
    with open("include/constants/global.h", 'r') as file:
        content = file.read()
    if '//#include "constants/versioning.h"' in content:
        content = content.replace('//#include "constants/versioning.h"', '#include "constants/versioning.h"')
        with open("include/constants/global.h", 'w') as file:
            file.write(content)
        out("Updated include/constants/global.h")
    makeSaveVersionConstants()
    out("Successfully applied the necessary changes to the codebase.")
    out("You will currently be unable to load previous save files until you make a new release.")
    out("Even if you delay this in function of more saveblock changes, you will be able to play with newly created save files.")

def failTustinInjection(msg):
    out(msg)
    # remove the latest versioning backups
    os.remove("versioning/global_v%s.c" % globalVersion)
    os.remove("versioning/pokemon_storage_system_v%s.c" % globalVersion)
    os.remove("versioning/sectors_v%s.txt" % globalVersion)
    quit()

# the following function defines all the save versions constants
def makeSaveVersionConstants():
    content = "#ifndef GUARD_CONSTANTS_VERSIONING_H\n#define GUARD_CONSTANTS_VERSIONING_H\n\n"
    for x in range(globalVersion + 1):
        content += "#define SAVE_VERSION_%s %s\n" % (x, x)
    content += "\n#define SAVE_VERSION (SAVE_VERSION_%s)\n\n#endif // GUARD_CONSTANTS_VERSIONING_H\n" % globalVersion
    # write to file
    with open("include/constants/versioning.h", 'w') as file:
        file.write(content)
    out("Updated include/constants/versioning.h")

def updateSwitchVersion():
    switchcase = ""
    includelist = ""
    for x in range(globalVersion):
        switchcase += "        case %s: // Upgrading from version %s to version %s\n            result = UpdateSave_v%s_v%s(gRamSaveSectorLocations);\n            break;\n" % (x, x, globalVersion, x, globalVersion)
        includelist += '#include "data/old_saves/save.v%s.h"\n' % x

    with open("src/save.c", 'r') as file:
        content = file.read()
        ncontent = re.sub("(\/\/ START Attempt to update the save\n    switch \(version\)\n    {\n)[^}]*(        default: \/\/ Unsupported version to upgrade\n            result = FALSE;\n            break;)", "\\1" + switchcase + "\\2", content)
        if content == ncontent:
            out("Error: unable to update src/save.c (switch case)!")
            quit()
        content = ncontent
        ncontent = re.sub("(\/\/ START Include old save data\n)[\s\S]*?(\/\/ END Include old save data)", "\\1" + includelist + "\\2", content)
        if content == ncontent:
            out("Error: unable to update src/save.c (include list)!")
            quit()
    with open("src/save.c", 'w') as file:
        file.write(ncontent)
    out("Updated src/save.c")

# alternative of plain old "print" that allows for logging
def out(str):
    print(str)
    if '--log' in sys.argv:
        f.write(str + '\n')

# a hacky solution that replaces enums with their actual values, allowing the Evaluator to deal with it
def parse_size(tokens, enumlist):
    sizetokens = ""
    e = Evaluator()
    for x in tokens:
        if x.value in enumlist:
            sizetokens += str(enumlist[x.value])
        else:
            sizetokens += str(x.value)
    return e(sizetokens)

def parse_field(field, enumlist):
    cl = {}
    cl['name'] = field.name
    cl['type'] = field.type.__class__.__name__
    if (cl['type'] == "Type"):
        if hasattr(field.type.typename.segments[0], 'name'):
            cl['kind'] = field.type.typename.segments[0].name
        else:
            cl['kind'] = "__AnonymousName%s" % field.type.typename.segments[0].id
        cl['is_struct'] = (field.type.typename.classkey == 'struct')
        if field.type.typename.classkey == 'union':
            cl['is_union'] = True
    elif (cl['type'] == "Array"):
        if (field.type.array_of.__class__.__name__ == "Type"): #1D ARRAY
            cl['kind'] = field.type.array_of.typename.segments[0].name
            cl['is_struct'] = (field.type.array_of.typename.classkey == 'struct')
        elif (field.type.array_of.__class__.__name__ == "Array"):
            if (field.type.array_of.array_of.__class__.__name__ == "Type"): #2D ARRAY
                cl['kind'] = field.type.array_of.array_of.typename.segments[0].name
                cl['is_struct'] = (field.type.array_of.array_of.typename.classkey == 'struct')
            elif (field.type.array_of.__class__.__name__ == "Array"): #3D ARRAY
                cl['kind'] = field.type.array_of.array_of.array_of.typename.segments[0].name
                cl['is_struct'] = (field.type.array_of.array_of.array_of.typename.classkey == 'struct')
    elif (cl['type'] == "Pointer"):
        cl['kind'] = field.type.ptr_to.typename.segments[0].name
        cl['is_pointer'] = True
    if hasattr(field.type, 'size'):
        cl['size'] = parse_size(field.type.size.tokens, enumlist)
    if hasattr(field.type, 'array_of'):
        if hasattr(field.type.array_of, 'size'):
            cl['size2'] = parse_size(field.type.array_of.size.tokens, enumlist)
        if hasattr(field.type.array_of, 'array_of'):
            if hasattr(field.type.array_of.array_of, 'size'):
                cl['size3'] = parse_size(field.type.array_of.array_of.size.tokens, enumlist)
    if (field.bits != None):
        cl['bits'] = field.bits
    return(cl)

def parse_file2(path):
    out = parse_file(path)
    enum_out = {}
    for x in out.namespace.enums:
        val = 0
        for y in x.values:
            enum_out[y.name] = val
            val += 1
    return(out, enum_out)

def compareFields(fieldname, inline, extratext):
    extratext_display = ""
    if extratext != "":
        extratext_display = " (%s)" % extratext

    if fieldname not in GlobalClassesNew:
        invalid_resolve = True
        # check if exists in GlobalClassesOld
        if fieldname not in GlobalClassesOld:
            # fieldname can not be found, so check if it's in both referals
            if fieldname in GlobalReferNew and fieldname in GlobalReferOld:
                if GlobalReferNew[fieldname] == GlobalReferOld[fieldname]:
                    fieldname = GlobalReferNew[fieldname] # get referral (eg lilycovelady > anonymousname...)
                    invalid_resolve = False
        if invalid_resolve:
            out("WARNING: Unable to resolve %s%s" % (fieldname, extratext_display))
            return
    # make list of fields
    fields_old = {}
    fields_old_array = []
    for x in GlobalClassesOld[fieldname].fields:
        fields_old[x.name] = x
        fields_old_array.append(x.name)

    # compare
    global globalHasChanges
    global globalDifferences
    if '--verbose' in sys.argv or '--detailed' in sys.argv or (inline == 1):
        out("  " * (inline - 1) + "Comparing %s%s" % (fieldname, extratext_display))
    for x in GlobalClassesNew[fieldname].fields:
        if not x.name in fields_old:
            out("  " * inline  + "%s is a new field that was not present in the previous version" % x.name)
            globalHasChanges = True
            if not fieldname in globalDifferences:
                globalDifferences.append(fieldname)
            continue
        oldclass = parse_field(fields_old[x.name], GlobalEnumsOld)
        newclass = parse_field(x, GlobalEnumsNew)

        if (x.name in fields_old_array):
            fields_old_array.remove(x.name)
            if (x == fields_old[x.name]):
                if '--verbose' in sys.argv:
                    out("  " * inline + "%s is identical" % x.name)
                # if identical, check the actual kind to make sure the underlying struct didn't change
                if newclass['kind'] not in trusted_typedefs.keys():
                    compareFields(newclass['kind'], inline + 1, "%s -> %s" % (extratext, x.name))
                continue
            # figure out what exactly is different, starting with size
            globalHasChanges = True
            if 'size' in newclass and 'size' in oldclass:
                oldsize = int(oldclass['size'])
                newsize = int(newclass['size'])
                if (oldsize != newsize):
                    if (oldsize < newsize):
                        out("  " * inline + "%s was expanded in size from %s to %s" % (x.name, oldsize, newsize))
                    else:
                        out("  " * inline + "IMPORTANT: %s was truncated in size from %s to %s" % (x.name, oldsize, newsize))
                    continue
            out("  " * inline + "%s is different, but can't identify why!" % x.name)
        else:
            out("  " * inline + "%s is a new field; defaulting values to zero" % x.name)

    if len(fields_old_array) > 0:
        out("  " * inline + "The following old fields are not retained: %s" % fields_old_array)

def prepare_comparison(filename, starting_version):
    global GlobalClassesOld
    global GlobalClassesNew
    contents_old, enums_old = parse_file2('versioning/%s_v%s.c' % (filename, starting_version))
    contents_new, enums_new = parse_file2('versioning/%s_v%s.c' % (filename, globalVersion))

    # classes
    for x in contents_old.namespace.classes:
        if hasattr(x.class_decl.typename.segments[0], 'name'):
            GlobalClassesOld[x.class_decl.typename.segments[0].name] = x
        else:
            GlobalClassesOld["__AnonymousName%s" % x.class_decl.typename.segments[0].id] = x
        for y in x.classes:
            if hasattr(y.class_decl.typename.segments[0], 'name'):
                GlobalClassesOld[y.class_decl.typename.segments[0].name] = y
            else:
                GlobalClassesOld["__AnonymousName%s" % y.class_decl.typename.segments[0].id] = y
    for x in contents_new.namespace.classes:
        if hasattr(x.class_decl.typename.segments[0], 'name'):
            GlobalClassesNew[x.class_decl.typename.segments[0].name] = x
        else:
            GlobalClassesNew["__AnonymousName%s" % x.class_decl.typename.segments[0].id] = x
        for y in x.classes:
            if hasattr(y.class_decl.typename.segments[0], 'name'):
                GlobalClassesNew[y.class_decl.typename.segments[0].name] = y
            else:
                GlobalClassesNew["__AnonymousName%s" % y.class_decl.typename.segments[0].id] = y
    # typedefs (for referals)
    for x in contents_old.namespace.typedefs:
        if hasattr(x.type, 'typename'):
            if x.type.typename.classkey != None:
                if hasattr(x.type.typename.segments[0], 'name'):
                    if x.type.typename.segments[0].name != x.name:
                        GlobalReferOld[x.name] = x.type.typename.segments[0].name
                else:
                    GlobalReferOld[x.name] = "__AnonymousName%s" % x.type.typename.segments[0].id
    for x in contents_new.namespace.typedefs:
        if hasattr(x.type, 'typename'):
            if x.type.typename.classkey != None:
                if hasattr(x.type.typename.segments[0], 'name'):
                    if x.type.typename.segments[0].name != x.name:
                        GlobalReferNew[x.name] = x.type.typename.segments[0].name
                else:
                    GlobalReferNew[x.name] = "__AnonymousName%s" % x.type.typename.segments[0].id
    return(enums_old, enums_new)

def prepareMigration(listofchanges, versionnumber):
    # get sector ids
    with open("versioning/sectors_v%s.txt" % versionnumber, 'r') as file:
        sectorids = file.read().split("\n")
    # content header
    content = '#include "global.h"\n#include "save.h"\n\n// This file contains the backups for the save file of v%s.\n// Editing this file may cause unwanted behaviour.\n// Please use make release in case problems arise.\n\n' % versionnumber
    # add actual backups
    for x in listofchanges:
        content += backupDump(x, versionnumber, listofchanges)

    # add migration function
    content += "\nbool8 UpdateSave_v%s_v%s(const struct SaveSectorLocation *locations)\n{\n" % (versionnumber, globalVersion)
    # add const structs
    if 'SaveBlock2' in listofchanges:
        content += "    const struct SaveBlock2_v%s* sOldSaveBlock2Ptr = (struct SaveBlock2_v%s*)(locations[%s].data); // SECTOR_ID_SAVEBLOCK2\n" % (versionnumber, versionnumber, sectorids[0])
    else:
        content += "    const struct SaveBlock2* sOldSaveBlock2Ptr = (struct SaveBlock2*)(locations[%s].data); // SECTOR_ID_SAVEBLOCK2\n" % (sectorids[0])
    if 'SaveBlock1' in listofchanges:
        content += "    const struct SaveBlock1_v%s* sOldSaveBlock1Ptr = (struct SaveBlock1_v%s*)(locations[%s].data); // SECTOR_ID_SAVEBLOCK1_START\n" % (versionnumber, versionnumber, sectorids[1])
    else:
        content += "    const struct SaveBlock1* sOldSaveBlock1Ptr = (struct SaveBlock1*)(locations[%s].data); // SECTOR_ID_SAVEBLOCK1_START\n" % (sectorids[1])
    if 'PokemonStorage' in listofchanges:
        content += "    const struct PokemonStorage_v%s* sOldPokemonStoragePtr = (struct PokemonStorage_v%s*)(locations[%s].data); // SECTOR_ID_PKMN_STORAGE_START\n" % (versionnumber, versionnumber, sectorids[2])
    else:
        content += "    const struct PokemonStorage* sOldPokemonStoragePtr = (struct PokemonStorage*)(locations[%s].data); // SECTOR_ID_PKMN_STORAGE_START\n" % (sectorids[2])
    content += "    u32 arg, i, j, k;\n\n"

    # saveblock2
    content += "    // SaveBlock2 \n"

    if not 'SaveBlock2' in listofchanges:
        content += "    *gSaveBlock2Ptr = *sOldSaveBlock2Ptr;\n"
    else:
        content += dealWithMigration('SaveBlock2')

    # saveblock1
    content += "\n    // SaveBlock1 \n"

    if not 'SaveBlock1' in listofchanges:
        content += "    *gSaveBlock1Ptr = *sOldSaveBlock1Ptr;\n"
    else:
        content += dealWithMigration('SaveBlock1')

    # pokemonstorage
    content += "\n    // PokemonStorage \n"

    if not 'PokemonStorage' in listofchanges:
        content += "    *gPokemonStoragePtr = *sOldPokemonStoragePtr;\n"
    else:
        content += dealWithMigration('PokemonStorage')

    # take care of continue game warp
    content += "\n    SetContinueGameWarpStatus();\n    gSaveBlock1Ptr->continueGameWarp = gSaveBlock1Ptr->lastHealLocation;\n\n    return TRUE;\n}\n"

    # write it to file
    with open("src/data/old_saves/save.v%s.h" % versionnumber, 'w') as file:
        file.write(content)
    out("Added migration support from version %s to version %s (src/data/old_saves/save.v%s.h)" % (versionnumber, globalVersion, versionnumber))

def fetchDefineValue(name, code):
    z = re.findall('#define %s *(.*)' % name, code)
    if len(z) == 1:
        return z[0]
    return None

def dealWithMigration(name):
    out = "#define COPY_FIELD(field) g{st}Ptr->field = sOld{st}Ptr->field\n#define COPY_BLOCK(field) CpuCopy16(&sOld{st}Ptr->field, &g{st}Ptr->field, sizeof(g{st}Ptr->field))\n#define COPY_ARRAY(field) for(i = 0; i < min(ARRAY_COUNT(g{st}Ptr->field), ARRAY_COUNT(sOld{st}Ptr->field)); i++) g{st}Ptr->field[i] = sOld{st}Ptr->field[i];\n\n".format(st=name)
    for field in GlobalClassesNew[name].fields:
        # hardcoded feature to make save migration work
        if (name == "SaveBlock2" and field.name in ['_saveSentinel', 'saveVersion']):
            if field.name == '_saveSentinel':
                out += "    gSaveBlock2Ptr->_saveSentinel = 0xFF;\n"
            if field.name == 'saveVersion':
                out += "    gSaveBlock2Ptr->saveVersion = %s;\n" % globalVersion
            continue
        # if not present in the old save, we can't carry it over so it defaults to zero
        if not field in GlobalClassesOld[name].fields:
            continue
        # ignore map-based save stuff
        if (field.name in ignored_map_fields):
            continue
        # check other fields
        # add check to see if it actually stays the same here later
        if (field.type.__class__.__name__ == "Array"):
            if (field.type.array_of.__class__.__name__ == "Array"):
                out += "    COPY_BLOCK(%s);\n" % field.name
                continue
            elif (field.type.array_of.__class__.__name__ == "Type"):
                if (field.type.array_of.typename.classkey == "struct"):
                    out += "    COPY_BLOCK(%s);\n" % field.name
                    continue
            out += "    COPY_ARRAY(%s);\n" % field.name
        else:
            out += "    COPY_FIELD(%s);\n" % field.name
    return out + "\n#undef COPY_FIELD\n#undef COPY_BLOCK\n#undef COPY_ARRAY\n"

def backupDump(structname, versionnumber, listofchanges):
    # we make a struct and add its components
    out = "struct %s_v%s\n{\n" % (structname, versionnumber)
    for field in GlobalClassesOld[structname].fields:
        out += "    "
        # we cycle through arrays of arrays until we find the relevant information
        field_type = field.type
        while (field_type.__class__.__name__ == "Array"):
            field_type = field_type.array_of
        # add "struct" etc if necessary
        if field_type.typename.classkey != None:
            out += "%s " % field_type.typename.classkey
        out += field_type.typename.segments[0].name
        # if the referenced struct is different from the modern one, refer to the old one
        if field_type.typename.segments[0].name in listofchanges and field_type.typename.segments[0].name not in trusted_typedefs:
            out += "_v%s" % versionnumber
        out += " %s" % field.name
        # add sizes for arrays
        field_type = field.type
        while hasattr(field_type, 'size'):
            out += "[%s]" % int(parse_size(field_type.size.tokens, GlobalEnumsOld))
            if (field_type.__class__.__name__ == "Array"):
                field_type = field_type.array_of
            else:
                break
        # add bits if necessary
        if field.bits != None:
            out += ":%s" % field.bits
        out += ";\n"
    return (out + "};\n\n")

if __name__ == "__main__":
    if '--log' in sys.argv:
        f = open('log.txt', 'w')
    
    pull_new_version()
    # use cxxheaderparser to figure out everything
    GlobalClassesOld = {}
    GlobalClassesNew = {}

    GlobalReferOld = {}
    GlobalReferNew = {}

    # first compare the current state of affairs with the latest version. only if this is changed (see globalHasChanges) do we need to recompare with the older changes
    GlobalEnumsOld, GlobalEnumsNew = prepare_comparison('global', globalVersion - 1)
    prepare_comparison('pokemon_storage_system', globalVersion - 1) # no enum output because this file doesn't contain any

    compareFields('SaveBlock2', 1, 'gSaveBlock2Ptr')
    compareFields('SaveBlock1', 1, 'gSaveBlock1Ptr')
    compareFields('PokemonStorage', 1, 'gPokemonStoragePtr')
    # clean up if no changes
    if not globalHasChanges:
        out("No save migration needed!")
        os.remove("versioning/global_v%s.c" % globalVersion)
        os.remove("versioning/pokemon_storage_system_v%s.c" % globalVersion)
        os.remove("versioning/sectors_v%s.txt" % globalVersion)
    # prepare for actual upgrade otherwise
    else:
        # update constants and code
        makeSaveVersionConstants()
        updateSwitchVersion()
        # there is a new latest version, so we'll delete the src/data/old_saves folder and rebuild it from scratch
        if os.path.exists("src/data/old_saves/"):
            shutil.rmtree("src/data/old_saves/")
        os.mkdir("src/data/old_saves/")
        # start by updating the previous version to the current version
        prepareMigration(globalDifferences, globalVersion - 1)
        # loop through previous versions, compare and make migration scripts
        currentLoopingVersion = globalVersion - 2
        while (currentLoopingVersion >= 0):
            globalHasChanges = False
            globalDifferences = []
            GlobalEnumsOld, GlobalEnumsNew = prepare_comparison('global', currentLoopingVersion)
            prepare_comparison('pokemon_storage_system', currentLoopingVersion) # no enum output because this file doesn't contain any
            compareFields('SaveBlock2', 1, 'gSaveBlock2Ptr')
            compareFields('SaveBlock1', 1, 'gSaveBlock1Ptr')
            compareFields('PokemonStorage', 1, 'gPokemonStoragePtr')
            prepareMigration(globalDifferences, currentLoopingVersion)
            currentLoopingVersion -= 1

    if '--log' in sys.argv:
        f.close()

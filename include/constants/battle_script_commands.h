#ifndef GUARD_CONSTANTS_BATTLE_SCRIPT_COMMANDS_H
#define GUARD_CONSTANTS_BATTLE_SCRIPT_COMMANDS_H

// Battle Scripting and BattleCommunication addresses
#define sPAINSPLIT_HP gBattleScripting
#define sBIDE_DMG gBattleScripting + 4
#define sMULTIHIT_STRING gBattleScripting + 8
#define sEXP_CATCH gBattleScripting + 0xE
#define sTWOTURN_STRINGID gBattleScripting + 0xF
#define sB_ANIM_ARG1 gBattleScripting + 0x10
#define sB_ANIM_ARG2 gBattleScripting + 0x11
#define sTRIPLE_KICK_POWER gBattleScripting + 0x12
#define sMOVEEND_STATE gBattleScripting + 0x14
#define sBANK_WITH_ABILITY gBattleScripting + 0x15
#define sMULTIHIT_EFFECT gBattleScripting + 0x16
#define sBANK gBattleScripting + 0x17
#define sB_ANIM_TURN gBattleScripting + 0x18
#define sB_ANIM_TARGETS_HIT gBattleScripting + 0x19
#define sSTATCHANGER gBattleScripting + 0x1A
#define sSTAT_ANIM_PLAYED gBattleScripting + 0x1B
#define sGIVEEXP_STATE gBattleScripting + 0x1C
#define sBATTLE_STYLE gBattleScripting + 0x1D
#define sLVLBOX_STATE gBattleScripting + 0x1E
#define sLEARNMOVE_STATE gBattleScripting + 0x1F
#define sFIELD_20 gBattleScripting + 0x20
#define sRESHOW_MAIN_STATE gBattleScripting + 0x21
#define sRESHOW_HELPER_STATE gBattleScripting + 0x22
#define sFIELD_23 gBattleScripting + 0x23
#define sFIELD_24 gBattleScripting + 0x24
#define sMULTIPLAYER_ID gBattleScripting + 0x25
#define sMON_CAUGHT gBattleScripting + 0x26
#define sSAVED_DMG gBattleScripting + 0x28
#define sSAVED_MOVE_EFFECT gBattleScripting + 0x2C

#define cEFFECT_CHOOSER gBattleCommunication + 3
#define cMULTISTRING_CHOOSER gBattleCommunication + 5

// Battle Script defines for getting the wanted battler
#define BS_TARGET                   0
#define BS_ATTACKER                 1
#define BS_EFFECT_BATTLER           2
#define BS_FAINTED                  3
#define BS_BATTLER_0                7
#define BS_ATTACKER_WITH_PARTNER    4 // for atk98_status_icon_update
#define BS_ATTACKER_SIDE            8 // for atk1E_jumpifability
#define BS_NOT_ATTACKER_SIDE        9 // for atk1E_jumpifability
#define BS_SCRIPTING                10
#define BS_PLAYER1                  11
#define BS_OPPONENT1                12
#define BS_PLAYER2                  13
#define BS_OPPONENT2                14
#define BS_ABILITY_BATTLER			15

// atk 01, accuracy calc
#define NO_ACC_CALC_CHECK_LOCK_ON 0xFFFF
#define ACC_CURR_MOVE 0

// compare operands
#define CMP_EQUAL               0x0
#define CMP_NOT_EQUAL           0x1
#define CMP_GREATER_THAN        0x2
#define CMP_LESS_THAN           0x3
#define CMP_COMMON_BITS         0x4
#define CMP_NO_COMMON_BITS      0x5

// atk76, various
#define VARIOUS_CANCEL_MULTI_TURN_MOVES         0
#define VARIOUS_SET_MAGIC_COAT_TARGET           1
#define VARIOUS_IS_RUNNING_IMPOSSIBLE           2
#define VARIOUS_GET_MOVE_TARGET                 3
#define VARIOUS_RESET_INTIMIDATE_TRACE_BITS     5
#define VARIOUS_UPDATE_CHOICE_MOVE_ON_LVL_UP    6
#define VARIOUS_EMIT_YESNOBOX                   13
#define VARIOUS_WAIT_CRY                        18
#define VARIOUS_RETURN_OPPONENT_MON1            19
#define VARIOUS_RETURN_OPPONENT_MON2            20
#define VARIOUS_VOLUME_DOWN                     21
#define VARIOUS_VOLUME_UP                       22
#define VARIOUS_SET_TELEPORT_OUTCOME            25
#define VARIOUS_PLAY_TRAINER_DEFEATED_MUSIC     26
#define VARIOUS_STAT_TEXT_BUFFER                27
#define VARIOUS_SWITCHIN_ABILITIES              28
#define VARIOUS_SAVE_TARGET                     29
#define VARIOUS_RESTORE_TARGET                  30
#define VARIOUS_INSTANT_HP_DROP                 31
#define VARIOUS_CLEAR_STATUS                    32
#define VARIOUS_RESTORE_PP                      33
#define VARIOUS_TRY_ACTIVATE_MOXIE              34
#define VARIOUS_TRY_ACTIVATE_FELL_STINGER       35
#define VARIOUS_PLAY_MOVE_ANIMATION             36
#define VARIOUS_SET_LUCKY_CHANT                 37
#define VARIOUS_SUCKER_PUNCH_CHECK              38
#define VARIOUS_SET_SIMPLE_BEAM                 39
#define VARIOUS_TRY_ENTRAINMENT                 40
#define VARIOUS_SET_LAST_USED_ABILITY           41
#define VARIOUS_TRY_HEAL_PULSE                  42
#define VARIOUS_TRY_QUASH                       43
#define VARIOUS_INVERT_STAT_STAGES              44
#define VARIOUS_SET_TERRAIN                     45
#define VARIOUS_TRY_ME_FIRST                    46
#define VARIOUS_JUMP_IF_BATTLE_END              47
#define VARIOUS_TRY_ELECTRIFY                   48
#define VARIOUS_TRY_REFLECT_TYPE                49
#define VARIOUS_TRY_SOAK                        50
#define VARIOUS_HANDLE_MEGA_EVO					51
#define VARIOUS_TRY_LAST_RESORT					52
#define VARIOUS_ARGUMENT_STATUS_EFFECT			53
#define VARIOUS_TRY_HIT_SWITCH_TARGET			54
#define VARIOUS_TRY_AUTONOMIZE					55
#define VARIOUS_TRY_COPYCAT						56
#define VARIOUS_ABILITY_POPUP					57
#define VARIOUS_DEFOG							58
#define VARIOUS_JUMP_IF_TARGET_ALLY				59
#define VARIOUS_TRY_SYNCHRONOISE				60
#define VARIOUS_PSYCHO_SHIFT					61
#define VARIOUS_CURE_STATUS						62
#define VARIOUS_POWER_TRICK						63

// atk80, dmg manipulation
#define ATK80_DMG_CHANGE_SIGN                               0
#define ATK80_DMG_HALF_BY_TWO_NOT_MORE_THAN_HALF_MAX_HP     1
#define ATK80_DMG_DOUBLED                                   2
#define ATK80_1_8_TARGET_HP                                 3
#define ATK80_FULL_ATTACKER_HP                              4
#define ATK80_CURR_ATTACKER_HP                              5

// atk4F, a flag used for the jumpifcantswitch command
#define ATK4F_DONT_CHECK_STATUSES   0x80

// statchange defines
#define STAT_CHANGE_BS_PTR                  0x1
#define STAT_CHANGE_NOT_PROTECT_AFFECTED    0x20
#define STAT_CHANGE_WORKED      0
#define STAT_CHANGE_DIDNT_WORK  1

// atk48
#define ATK48_STAT_NEGATIVE         0x1
#define ATK48_STAT_BY_TWO           0x2
#define ATK48_ONLY_MULTIPLE         0x4
#define ATK48_DONT_CHECK_LOWER      0x8

#define BIT_HP                      0x1
#define BIT_ATK                     0x2
#define BIT_DEF                     0x4
#define BIT_SPEED                   0x8
#define BIT_SPATK                   0x10
#define BIT_SPDEF                   0x20
#define BIT_ACC                     0x40
#define BIT_EVASION                 0x80

#endif // GUARD_CONSTANTS_BATTLE_SCRIPT_COMMANDS_H

#ifndef GUARD_POKEDEX_H
#define GUARD_POKEDEX_H

extern u8 gUnusedPokedexU8;
extern void (*gPokedexVBlankCB)(void);

enum
{
    DEX_MODE_HOENN,
    DEX_MODE_NATIONAL
};

enum
{
    FLAG_GET_SEEN,
    FLAG_GET_CAUGHT,
    FLAG_SET_SEEN,
    FLAG_SET_CAUGHT
};

void ResetPokedex(void);
u16 GetPokedexHeightWeight(u16 species, u8 data);
u16 GetNationalPokedexCount(u8);
u16 GetHoennPokedexCount(u8);
u8 DisplayCaughtMonDexPage(u16 species, u32 otId, u32 personality);
s8 GetSetPokedexSeenFlag(u16 species, u8 caseID);
s8 GetSetPokedexCaughtFlag(u16 species, u8 caseID);
u16 GetPokedexFlagFirstSeen(u16 nationalDexNo);
u16 GetPokedexFlagFirstCaught(u16 nationalDexNo);
u16 CreateMonSpriteFromNationalDexNumber(u16, s16, s16, u16);
bool16 HasAllHoennMons(void);
void ResetPokedexScrollPositions(void);
bool16 HasAllMons(void);
void CB2_OpenPokedex(void);

#endif // GUARD_POKEDEX_H

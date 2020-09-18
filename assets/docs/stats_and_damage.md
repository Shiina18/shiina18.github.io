# stats_and_damage

Adapted from https://nichegamescom.files.wordpress.com/2018/10/stats_and_damage.pdf and raics' damage calculator

- **[STR] Strength**
  - 0.9 BASE ATTACK (OFFENSE) with str-based weapons *per point* (0.7 *for equipment bonuses*) the italic part is omitted below
  - 0.7 BASE ATTACK with dex-based weapons (0.5) 
  - 0.7 BASE DEFENSE (TOUGHNESS) (0.5)
- **[VIT] Vitality**
  - 1.1 BASE DEFENSE (0.9) 
- **[DEX] Dexterity**
  - 1.1 BASE ATTACK with dex-based weapons (0.9) 
  - 0.7 BASE ATTACK with str-based weapons (0.5)
  - 1% ACCURACY (0.8%) 
  - 1% EVADE (0.6%) 
- **[AGI] Agility**  
  - 1.2% ACCURACY (1%)  
- **[AVD] Avoidance**  
  - 1.2% EVADE (1%)  
  - 1.2% EVADE MAGIC (1%)  
- **[INT] Intelligence**  
  - 1 MAGIC ATTACK (1)  
  - 1.2% SPELL ACCURACY (0.8)  
- **[MND] Mind**  
  - 0.9 MAGIC ATTACK (0.6)  
  - 0.8 MAGIC DEFENSE (0.6)  
  - 1.2% SPELL ACCURACY (1%)  
  - 0.8% EVADE MAGIC (0.5%)  
- **[RES] Resistance**  
  - 1 MAGIC DEFENSE (1) 

A simplified version for damage calculation

1. BASE DAMAGE = max{0, (BASE ATTACK - BASE DEFENSE)}					
2. TOTAL DAMAGE = BASE DAMAGE x BASE MULTIPLIER + EXTRA DAMAGE - DEFENSE
	- BASE MULTIPLIER = 1 + DAMAGE BONUS - RESISTANCE. Truncated so that it lies between 0 and 2.5.
3. FINAL DAMAGE = max{1, (TOTAL DAMAGE x DAMAGE MULTIPLIER)}	

Note that if EXTRA DAMAGE - DEFENSE < 0, if will affect the total damage.

where

- Attacker's BASE ATTACK from his core stats is pitted against defender's BASE DEFENSE, applicable weapon skills and elemental augments add 4 damage or 3 defense per rank; racial skills add 5 damage per rank.
- DAMAGE BONUS (a percent number, 1 point for 1%) = weapon damage type bonus (e.g. slash 15 for 15%) + weapon racial bonus + weapon elemental bonus + resistence on jewelry
- RESISTANCE (a percent number) = damage type, racial and elemental resistance from armor, shield and jewelry
  - Many status will affect DAMAGE BONUS and RESISTANCE part, e.g. Strengthen, Breach.
- EXTRA DAMAGE = WEAPON ATTACK x 1.2 + JEWELRY ATTACK + CLASS ATTACK
- DEFENSE = ARMOR DEFENSE + SHIELD DEFENSE x 0.9 + JEWELRY DEFENSE + CLASS DEFENSE
- DAMAGE MULTIPLIER: for example, Mighty Impact = 1.5.

Magic damage is similar

- MAGIC ATTACK = BASE ATTACK
- MAGIC DEFENSE = BASE DEF
- SPELL INATE ATTACK = WEAPON ATTACK
- EXTRA DEF is the same with the physical

etc.
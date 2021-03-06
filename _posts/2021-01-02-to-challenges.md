---
title: "Tactics Ogre One Vision Mod Challenges"
categories: Games
updated: 2021-04-03
comments: true
mathjax: false
---

See [Game Log for Tactics Ogre LUCT One Vision Mod](https://shiina18.github.io/games/2020/07/17/game-log-for-to-ov-mod/) for the old post, and [this repo](https://github.com/Shiina18/tactics_ogre_one_vision_mod_challenges) for the rules and saves I used.

This time I am going to following the refined common rules and [optional rules](https://github.com/Shiina18/tactics_ogre_one_vision_mod_challenges#optional-rules), e.g. 5 skill 2 spell rule.

See [here](https://github.com/Shiina18/tactics_ogre_one_vision_mod_challenges/wiki/Meta-under-common-rules---optional-rules) for the meta under these rules.

2021/4/3: New rules are applied now, see [here](https://github.com/Shiina18/tactics_ogre_one_vision_mod_challenges/wiki/Experiment-Rules).

<!-- more -->

## Candidate builds

See [here](https://shiina18.github.io/games/2020/07/17/game-log-for-to-ov-mod/#teambuilding) for some of my thoughts about teambuilding.

Remember that this time **we only have 5 skill slots**, so every slot matters.

Format

```
Description for the build

- Equipment (1h weapon + shield by default)
- Skill 1
- Skill 2
- ...
```

Usually, **Spear sidegrade, Whip and ranged weapons are the best options for physical classes without magic.** See arguments [here](https://shiina18.github.io/games/2020/07/17/game-log-for-to-ov-mod/#teambuilding).

- Attacker (secondary attacker): can deal decent damage to most units.
- Wallbreaker (primary attacker): can deal decent damage to tanks (included in Attacker).
- Nuker: can eliminate units using high damage options (with the help of some combo).
- Support: can focus more on using their abilities to gain an advantage for the team. (typically can buff teammates or clean debuffs.)
- Annoyer: can inflict debuffs on enemies.
- Disabler: can inflict shutdown status on units with (nearly) 100% acc.
- Healer
- Tank

### Warrior

**Midline Wallbreaker, Nuker**

- 2H Spear sidegrade, AVD gears
- Spears
- Vigorous Attack
- Mighty Strike
- Double Strike
- Wade / Jump / Squash / Lead Ward / Rampart Aura

As a physical unit using melee weapons without magic, attack range and mobility matter. The 5th skill is decided by the map. Wade and Jump is for mobility. Sqaush removes clones made by Knight.

With a spear sidegrade, Counterhit is not needed. With Double Strike (so Bash is unwanted) and a 2h weapon, he can deal burst damage in one turn.

Considering that the spear provides some AVD, we may maximize AVD to make Warrior highly evasive. 

With an AVD build, Lead Ward will further raise Warrior's survivability and gives him an option to support teammates. As is often the case, Leaden will be inflicted by bow's rank 2 finisher or dark spell Wormhole.

Vigorous Attack may clear Stagger which is deadly to evasive units. With acc buff, AGI gears are not necessary for Warrior. Also, it is essential to tap Vigorous Attack beforehand to make sure Double Strike lands with (nearly) 100% acc. Due to Vigorous Attack, it is not very suitable for Warrior to use ranged weapons since Truestrike and Trueflight overwrite each other.

**Team Options**

- Melee fighters.
- Truestrike. Warrior may have some trouble generating the first 40 or 60 TP without AGI gears.
- Spike Skin. AI is foolish and will attack a unit with Spike Skin. This idea is provided by Vital who watched me use Spike Skin on some unit in a dangerous situation.

**Frontline or Midline Attacker**

- 1H Spear sidegrade, AVD gears or DEF gears
- Spears
- Vigorous Attack
- Mighty Strike
- 2 from Wade / Jump / Squash / Lead Ward / Rampart Aura / Field Alchemy

This build is much more defensive. With an 1h weapon, Warrior cannot deal much damage to tanks and instead focuses on hitting squishy units and supporting melee teammates with Vigorous Attack.

Mirror Aspis (Lv. 24 shield, 40 RES, 20% elem resist) is great to cover the hole of low magic def of Warrior.

**Other Options**

Of course, to make use of Mighty Strike, one might want to equip weapons possessing debuffs on hit. 

### Rogue

**Flank or Frontline Disabler / Annoyer**

- Blowgun, AVD gears
- Bullseye
- Other 4 skills don't matter and are optional, XX Ward / Sidearms / Tactician / Jump / Heron etc.

Bullseye is god. We need it for a guaranteed disable. 

I don't find it rewarding to use melee builds considering how squishy Rogue is and that he doesn't have magic. Sneak Attack is really useless.

Booby Trap is a very interesting skill if it's used by enemies. However, it requires consumables so are not very attractive under Heal Clause which restircts consumable uses.

Speedstar might be useful for a bow build, but not this one. In a disabler build, it is hard to generate enough TP to make Quick useful, and we want to tap Bullseye every time.

Counterhit shouldn't be equipped if a shutdown blowgun is used. Since by Shutdown Clause, it might lead to a sudden loss.

Non-shutdown blowguns (e.g. fear) are also useful and will be not restricted by Shutdown Clause.

**Team Options**

- Sidearm users (guaranteed Slow, Hobbled with the help of Bullseye).

### Tamer

**Frontline or Midline Ranged Attacker**

- Sidearm, AVD/DEF+AGI/DEX gears
- Sidearm
- Empower Monster
- Feral Remedy
- 2 from Trajectory / Monsterheart / Tactician

Ideally, Tamer should tap one skill every turn, and using a ranged weapon allows him to find a better position for both attacking and utilizing a skill in one turn.

```
Tamer extremely needs TP 
to use class skills every turn
-> high atk
    -> Sidearm. Tamer is tough, 
    so shorter range can be tolerated.
-> high acc
    -> AGI/DEX gears + Trajectory
Tactician helps to reach the TP threshold earlier, 
and also makes Turn 2 Trajectory possible.
```

**Team Options**

- Charge TP.
- Trueflight, e.g. Archer and classes having Ballistics (draconic).
- Strengthen. Remember that the output of DEX weapons will get more bonuses by the base damage part in calculation.
- Leaden.

### Bahamut (light dragon)

haven't tested it yet

**Support, Disabler, Nuker**

- Vit/Def Ring, No boulder
- Divine Magic
- Sacred Breath
- Disembowel
- haven't decided the left 2 slots yet

The sleep of Sacred Breath will be guaranteed with Dragonheart, so he can be called a disabler. ~~Holy War might not be handy to use due to Shutdown Clause~~ (shutdown clause is modified on 2021/1/21). 

Boulder might only be useful in high level or when the monster is empowered.

place holder

**Team Options**

- Light Averse. e.g Dark mages.

place holder

### Hoplite

haven't tested it yet

**Tank, Frontline Ranged Attacker**

- Sidearm, AGI + DEF gears
- Sidearm
- Check
- Rampart Aura
- 2 from Trajectory / Phanlanx / Tactician / Intersession

With Knight-like classes banned, the only tanks left are Hoplite and Golem.

Hoplite can't deal much damage and won't take much damage either, so TP generation is quite slow. 20 TP for Trajectory may be expensive for him, so AGI gears are needed.

With a sidearm, he can get a better position to stall enemies, attack and use a skill.

Rampart Aura (with or without Phanlanx) is a very powerful tool and there are a few tricks. I might talk about it in detail after finishing writing other parts.

Haven't used Intersession and Apostate much. Need some time to test.

**Team Options**

- Trueflight
  
### Warlock

This build is deprecated since Distill Mind is banned on 2021/1/20.

**Backline Utility Support / Annoyer / Disabler**

- MND/AVD gears
- Distill Mind
- Tactician
- Clarity
- 2 from Element Magic and Draconic Magic

The defining feature is Distill Mind, which makes Warlock the best Disabler / Support ever. Warlock can do anything well except dealing great damage. 

Clarity is always better than Efficacy if only one skill may be equipped. Tactician is here for Distill Mind. With these three skills, Warlock is never short of MP and can even charge MP to teammates.

If a disabler build is wanted, then my classic build can be applied: Dagger sidegrade + MND gears. With Class Clause Plus, the only shutdown option left for Warlock is a light spell, Oblivion. However, light magic sucks in general and can't coexist with dark magic where there are many debuffs available...

Build example: Lightning Magic + Draconic Magic. Use Draconic Magic to buff in Turn 2, and then tap Electrify to charge TP every turn.

### Berserker

**Dual Wielding Nuker**

- AGI/AVD gears
- Weapon skill
- Double Attack
- Last Resort
- 2 from Counterhit / Parry / Deflect / XX Ward / Jump

Self-explanatory build.

## Cressida challenge

2021/2/15

See the rules [here](https://github.com/Shiina18/tactics_ogre_one_vision_mod_challenges/wiki/Battlewise-challenges#cressida-challenge)

I will follow the reverse mirror match rules.

I'm going to follow 4 skills since 2021/3/13.

Classes available.

```
- FUSILIER	
- BEAST TAMER
- ROGUE
	
- SWORDMASTER (status restoration)
- DRAGOON	

- WIZARD
- SPELLBLADE
- LICH	

- JUGGERNAUT
- PATRIARCH
- FAMILIAR (status restoration)
- TRICKSTER 

- MONSTERS

- ARCHER (banned because of archers will show up in reinforcement)
```

Some candidates for the only one special class slot.

Wicce lv. 18

Exorcism, MP/TP control, Support

- Dagger sidegrade, DEF/VIT/AVD gears
- Draconic Magic
- Necromancy
- Devour
- Clarity

Necromancy and Devour are indispensable.

Due to the rules, there are only 2 consistent undead removal tools left: 
Banish from Necromancy and Fervor from White Knight.
As for Banish, there are only few classes left under the rules: 
Lich, Heretic, Wicce.

Besides Banish, Necromancy also provides important tools 
to remove MP (Brainrot) and TP (Curse).
Wicce has a not-too-bad accuracy 
(0.6 to Nebyth, 0.8 to Necro, 0.6 to Blue Witch, 0.75 to Blue TK, 0.6~0.7 to Blue Hoplite)
with max def build (VIT ring), 
spellcraft from Dagger sidegrade can guarantee 100%.
Using a MND ring or replacing Parry with Magic Time are also sound choices,
depending on builds of teammates.

Devour is for long ranged and reliable MP control. 
Devour can also be used to deal with Ninja's Nullify.

Draconic can take care of most minor status in one slot,
and offer damage and various support choices.
It can inflict any kind of elemental averse, 
which has synergy with damage scaling finishers from teammates.

Other options

Note that Devour also restores HP. 
A combo: Charge (MP) the enemy and then Devour him. 
The MP pool can be kept high 
and the process can be repeated again and again.

An option is to equip Empower Golem.

```
White Knight

- Palladium
- Fervor
- Santuary

Palladium + Santuary is possible to block enemies even in Obstacle Clause.
```

```
Commando

- Gambit

Since Divine Magic is banned, Gambit is the most convenient debuff removing tool.
```

Wizard lv. 18

Support: pure MP charger

- Book, AVD shield, Cloud Shoes, AVD ring
- Dark Magic
- Silence
- Meditate
- Clarity

Cloud Shoes provide Levitate which improves mage's poor movement, and Sidestep with which (and max avd gears) mage can evade ranged physical attack.

Books + Meditate + Clarity generate MP then use Charge to transfer it to others. The targets: Spellblade and Matriarch with 3 magic + evade.

Dark magic has quite a lot utility spells so he can also do something if Charge is not called for.

Other units may not have the slot to equip Silence Ward, so he has another job to clear silence for backlines.

Some thoughts for lv. 18 version

- Since some enemies have anatomy, better use demihumans as many as possible.
- Status: Silence, Stun, Bind, Shackle, Curse, Fear (TK and Night Crow in the reinforcement), Leaden, Bewitch
- Nybeth is fearsome, hitting 200+ damage with projectile 3. Drain Mind and spell def up might be needed for safety.
- Battering Ram, Flight, Squash, Absorb MP might be needed to take down the two necros. Waterwalk, xbows, guns might be needed to finish off Nybeth.


First team

- sg = sidegrade
- Weapon means the corresponding weapon skill

Candidates

- Wicce Dagger sg / Draco / Necro / Devour / Clarity or Empower
- Lich todo
- Swordmaster 2H Ka / Weapon / Aow / BladeFocus / Counterhit
- Trickster dual 1H Ka / Weapon / DoubleAttack / VampiricKiss / AbsorbMP or Dark
- Dragoner Thrown sg / Weapon / Traj / Empower / Remedy
- Dragon todo
- Wizard Book (AVD gear + Cloud Shoes) / Dark / SilenceWard / Meditate / Clarity
- Matriarch ? / Air / Water / Evade / Lightning or Clarity
- Spellblade Dagger / Lightning / Earth / AborbMP / FatedCircle
- Rogue A Fear Blowgun / Weapon / SilenceWard / Bullseye / Tactician
- Rogue B Heal Blowgun / CurseWard or other ward / BoobyTrap / Speedstar / Heron
- Familiar Book / Weapon / LingeringKiss / SelflessKiss / Sanctuary
- Golem Boulder + RES ring / VoidCore / Phalanx / Gordian / Rampart

Offensive cores

- General support: LionDance / Galvanize / Draco, HoverDraft
- Electrify + Empower + Disembowel
- Electrify + 2H Ka double hit finisher
- Dual Wielding

Niche combo

- Wizard Charge (Books + Meditate + Clarity) -> Spellblade + Matriarch (+ Wicce / Lich)

Roles

- Nuker: Dragon (Disembowel), Swordmaster (2H ka double hit)
- Primary attacker: Trickster (dual 1h ka)
- Secondary attacker: Dragoner, Familiar
- Debuff removal: Swordmaster, Familiar, Wicce (all minor debuffs)
- Healer: Rogue B, Swordmaster, Matriarch, Familiar
- Exorcism: Wicce, Lich

## Random thoughts

Core: archer (2h bow sidegrade + double shot) + familiar (selfless kiss) or Accelerator + Eletrify

- According to the mechanism of double shot, sidegrade bow is suited for the largest attacking area.
- With the help of Strengthen, 4 shots in a row should be enough to KO a non-tank unit. The problem is to avoid critical hit, so the standing location of the target is important. To that end, making an ally standing behind the target or putting an obstacle might be useful.
- Accelerator is much slower than the kiss (RT 80 vs 25). However, MP is much easier to generate than TP. In order to generate TP while stay near the archer in the backline, familiar might equip a bow as well.
- 2h bow sidegrade is slow. Suppose the first double shot deals 200 damage, then there is still 150 TP left to be generated, which takes time. Though TP can be obtained easier by consumables (50 or 100 for a trap), but abusing consumables means cheating in my mind.

## Interesting Battles

New rules are applied now, see [here](https://github.com/Shiina18/tactics_ogre_one_vision_mod_challenges/wiki/Experiment-Rules).

### The Gates of Barnicia

2021/4/3

- Version: 0.970c
- Enemy: 13 units with 1 Cleric, Level 20, Rank 4.
- Player: up to 12, but only used 9. Level 20, Rank 4. No cleric due to the rule.

Points

- It is the first battle for experimenting rules. The code only nerfs healing tools for the player, and tools used by AI are barely affected. Also Electrify is nerfed.
- Enemies have poor gears, and it is extremely easy to vanquish them all even without any heals. Last time I used 10 lv.18 units (rank 6) with poorest classes and that was far more difficult. Maybe I should try to use only 8 or 7 units, or just use lv. 18 ones.
- They have 5 archers and 4 mages, so the goal is to counter those.

Team

- Warlock: Book / Water / Silence Ward / Distill Mind / Clarity
- Ninja: Fist side + Vritra (Falseflight) / Weapon (Sidearm) / Deflect / Aow / Wild Hunt
- Archer: 2H Bow side / Weapon / Aow / Tremendous Shot / Double Shot
- Wicce: Dagger side / Draconic / Necro / Devour / Clarity
- Knight: 1H Sword + Stun Shield / Divine / Silence Ward / Aegis / Rampart
- Blade Knight: 2H Katana / Weapon / Deflect / Aow / Instill
- Trickster: 1H Katana side + 1H Katana / Weapon / Deflect / Double Attack / Vampiric Kiss
- Spellblade: Dagger / Weapon / Ice / Fire / Fated Circle
- Vartan: Thrown / Weapon / Instill / Huapango / El Colas

Game plan

- Use Deflect, Sidestep (Haze) and Resilient (Solidify) to counter archers and mages.
- Ninja and Archer spam Silence. Wicce use Brainrot and Devour to shut down mages.
- Offensive cores: Trickster + Blade Knight. Use Strengthen (Enlarge) to buff them and units with ranged weapons.

Issues

- Wild Hunt, Double Shot, Aegis, Huapango, El Colas are not used this time.
- When Decoy is on, Instill will be blocked, so be careful.

Thoughts

- The enemy mages barely have chance to cast any spell in fact.
- Trickster's movement type floating is great on a field full of tar. Also he has 6 movement, and higher MND. These facts make him a better choice over a berserker.
- 2H Bow side is much better than thought.
- This Wicce build is strikingly good. Use Brainrot to shut down multiple mages and then tap Devour to clear Knight's MP, so that enemies will have a hard time removing status.
- Rank 2 Bow finsher is deadly as thought. Be careful not to be hit by it.
- I will redo the battle with lv. 18 units. One major difference is that I don't have access to Vritra then. And we will have one tier lower gears.
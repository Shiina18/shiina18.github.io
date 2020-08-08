---
title: "Game Log for Tactics Ogre LUCT One Vision Mod"
categories: Games
updated: 2020-08-08
comments: true
mathjax: true
---

## Review on Tactics Ogre Vanilla

> Tactics Ogre is a hard game for me to talk about. I really wanted to love it, but the gameplay is so rotten at the base level that it undermines the entire game. But first, lets talk about the good stuff (I'm talking about the PSP version btw).
> <!-- more -->
> The world building, story / plot and chracter development is phenomenal. Matsuno, as usual, delivers here. The characters are deep and interesting, the plot mature, with lot's of political backstabing. The world building is probably the best in a game of the genre.
> 
> Akihiko Yoshida's art is beautiful and lend itself perfectly to the tone of the game. I wish he worked on Fire Emblem, much better than what we got now.
> 
> Hitoshi Sakamoto's sountrack is also great as usual, with themes that fit perfectly. "Revolt" is so classic that it instantly reminds me of Ogre Battle.
> 
> But then we come to the gameplay. It's simply put, a mess. Where to begin?
> 
> First, the stats and calculations system is completely overdesigned and still to this day people don't know how it works exactly. But that's not the worst. Small changes in any stat causes huge variations in damage done and received. This means that if your character is even 1 level above or behind the enemy, you will either stomp or be stomped. There's too much emphasys on stats here to the point of undermining tactical and strategic considerations.
> 
> Then you have the skill system. You basically have to grind a lot to unlock skills, and the grinding is per character. The skill system is also completely overdesigned, with many skills just being stronger versions of previous ones. Other don't seem to work at all.
> 
> While the map layouts are interesting, with a lot of verticality, mission objectives are incredibly dull and just boil down to wiping out enemy forces. All maps play exact the same: march forward and meet with the enemy.
> 
> The class and level system is also poorly designed (PSP version here). Your characters don't have levels, your unlocked classes do. So picture this: you are at the middle of the game, with classes in the 10 level range. Then you unlock a new one, and naturally, want to try it. But is starts at level 1, making any character at that class completely useless in combat. You must do random battles, leave said unit in a corner and completel the map with your other units so it can leech exp. Completely boring and unacceptable.
> 
> There's more, such as the crafting system being the worst I've yet to see in a game. Sigh.
> 
> Anyway, my point is: everything about it is great, except the gameplay. My suggestion is to just watch a playthrough for the plot and characters. Don't bother suffering through it. To make matters worse, Square Enix did an epic release trailer for the game, which is pure fan service for fans of the Ogre Battle world. See here: https://www.youtube.com/watch?v=ZZIt4d-j9oo
> 
> Now, if you like SRPGs focused on grinding and sandboxish elements, where it's about creating broke combination of units that can stomp everything... by all means play it. It certainly isn't fun to me.
>
> Source: [From the perspective of a Fire Emblem fan, how does Tactics Ogre compare : fireemblem](https://www.reddit.com/r/fireemblem/comments/33iwys/from_the_perspective_of_a_fire_emblem_fan_how/)

Having played *Tactics Ogre: Let Us Cling Together* (PSP remake) and *Tactics Ogre: The Knight of Lodis* (GBA) many years ago, I couldn't agree more with the comment cited above. TO is a rather easy game. 

- AI design: For every attack turn, a unit has too many options available while the simply designed AI just can't make a good choice. In contrast, in FE, very limited options are given. As a result, enemies are threatening even though they behave according to some very simple rules. They are threatening partly because player's team and AI's take turns as a whole not by character-wise, which makes killing a unit much easier (no FE core player would tolerate character death).
- Map design: TO's maps are cool but those interesting elements are just not expoited at all. While FE's maps are very well designed and even the grids are deliberately calculated (you may find many examples in *Fire Emblem Fates: Conquest*). Almost every components are made use of.

A detailed review can be found on [タクティクスオウガ 運命の輪 - ゲームカタログ@Wiki ～名作からクソゲーまで～ - アットウィキ](https://w.atwiki.jp/gcmatome/?cmd=word&word=タクティクスオウガ&type=&pageid=4623).

## One Vision Mod

I came across this mod one year ago when I wanted to figure out how the damage is calculated on earth, since it is really mysterious and confused me for many years. I searched in Japanese at first but failed to find any useful information. Then I tried in English and reached the calculation breakdown sheet. I noticed that the author had a mod called OV. I played with it and liked it very much. It fullfils my imagination when I first played this game years ago. So I began to propagate it in Chinese community. Now there are several people having played with this mod in China. While most are just scared away for being unable to read English.

The information for OV mod can be found [here](https://www.moddb.com/mods/one-vision1).

## Playing Log

### Self-imposed Challenges

The following clauses aim at making the game more difficult. This is called「縛りプレイ」in Japanese.

> 様々な要素からゲームを今クリアするだけなら難易度が低いゲームに対し、自主的な制限をつけることで敢えて難易度を引き上げ、やりごたえのあるゲームを自ら作り上げる、と言うのが縛りプレイの主な趣旨である。Source: [ニコニコ大百科](https://dic.nicovideo.jp/a/%E7%B8%9B%E3%82%8A%E3%83%97%E3%83%AC%E3%82%A4)

- **Class Clause**
    - The player cannot have two units with the same class on a team.
    - A team cannot have more than three units with special classes. Any wingedman is counted as special no matter what class he is.
    - Denam must be Warrior. 
- **Objection Clause**
    - If there are reinforcements,
        - the boss can only be killed when (1) reinforcements run out and (2) $\text{# of enemies} \le\min\\{5, \text{# of allies}\\}$ (since killing Knights and Golems might be too time consuming);
    - Else,
        - the boss can only be killed when other enemies are killed.
- **Grinding Clause**
    - Grinding for experience is not allowed.
    - Highest level in player's party $\le$ lowest level in enemies.
- **Tarot Clause**
    - No Chariot Tarot for retracing steps. 
    - No Tarot card stat bonus.

```
_C1 No Tarot Stat Bonus
_L 0x20025C28 0x34060000
_L 0x20025C34 0x34060000
```

- **Heal Clause** - The number of times of using healing magic, skills and weapons $\le$ (1 + # of enemy clerics) $\times$ [# of total enemy units / 3]. And this upper bound is denoted as $N$. 
    - For example, if an enemy team consists of 11 units including 2 clerics then $N = (1+2) \times [11/3] = 3\times 3 = 9$. 
    - Healing magic, skills and weapons include Heal, Allheal (Light AOE Heal), Harvest Dance (Art of War), Purify (Water AOE Heal + Cleanse), HP Infusion (Spellblade TP to HP), Time of Need (White Knight AOE TP to HP), Instill HP (Warlock), Kirin Blowgun, etc. 
    - Those granting Renewal are not included. Lancet (Dark HP to HP) is not included since it's fair. Drain Heart (Dark) and magic like that which drains HP from others are not included.

- **Consumeble Clause** - The number of times of using consumebles $\le [N/2]$.
- **Stop Ward Clause** - Equipping the skill Stop Ward is prohibited.

### For This Run

Given that I refuse to use special classes as often, I would argue that **Cleric** and **Knight** are the most prominent classes: Cleric is the only general class that has access to Heal and Knight is central for defensive purpose (highest HP and DEF + status restoration magic + Rampart Aura + Phanlanx); and they are gods when battling with the undead. **Terror Knight** and **Warlock** are also of great importance: Terror Knight is good at countering Knight (Frighten + Shadow Break) and is also capable of shutting down magicians (Drain Mind, especially useful for bosses); Warlock can shut down others consistently, making the battle much easier according to [Lanchester's laws](https://en.wikipedia.org/wiki/Lanchester%27s_laws).

To make the game further harder, I would only use classes available at the very beginning of the game, with Terror Knight not being included. And I will give the Tamer + Dragon combo a shot.

### Interesting Battles 

#### The Gates of Almorica Castle at Chapter 2 Route C

- Version: 0.960
- Targets: Xapan and Ramidos (main target). 
- Enemy: 12 + 6, including 2 Clerics. Level 11.
- Player: 10. Level 11.

##### Teambuilding

1. **Warrior (Denam)** Spear with range 2-3

**For classes without magic, it is essential to have high attack range so that the unit can have more opportunities to make an impact on the battlefield.** To give some insight, suppose the move range + attack range = $n$, then the attainable area is $2n^2 + 2n + 1$, ignoring terrain. In this case, move range 5 + attack range 3 = 8, attainable area = 145; while if $n=5+1=6$, then attainable area = 85, which is way smaller.

In order to employ class skills, melee weapons are favored. So a spear with range 2-3 is chosen.

2. **Archer (General Female)** 2-H Bow

Their main attacking targets are casters and archers. Bows are favored given that Crossbows will often be blocked.

Using Bridle to mute magicians is crucial.

2-H Bows are chosen for higher attack range and atk. Archers will typically be killed by archers and magicians, so better stay in a safe place.

3. **Wizard (General Male)** Dark and Ice Magic

Dark magic provides an arsenal for controlling in early game.

TP controlling is important. Players should avoid being hit by finishing moves. Ice magic Frostbite is handy for that.

4. **Cleric (Donnalto)** Fist; Absorb MP

Fists are light and 1-H, and provide some AVD bonus, so are favored.

Cleric wears light armor to lower RT and to attract some attack. 

Absorb MP: You can drain alley magician's MP when needed.

5. **Spellblade (Cistina)** Dagger; Air, Water Magic

This build is for controlling and supporting purposes.

Dagger is used together with Fated Circle to bind enemies. Rank 2 finishing move is also useful to shutdown magicians and to gain MP in the same time.

Air for Grace and flight, Water for healing.

Grace (melee avd up) will be used in Turn 1, and Fated Circle will be used from Turn 2.

Spellblade wears heavy armor. With HP Infusion (and Spike Skin), they can be really tough so more DEF is favored.

6. **Knight (Voltare)** Sword

There is no adequate reason for swords. Other options also work.

One advantage is that sword has 2-H variant which is counted as 1-H, so Knight may use 2-H variant to maximize damage (with rank 2 finishing move or Instill Light).

**Unnessary battles should be avoided for TP controlling purpose so that the enemy can't use finishing moves or critical skills frequently.** Typically, Knights should prioritize restoring status for others rather than attacking. Attacking leads to TP accumulation for the target and a counterhit from him which results in HP reduction for the attacker. With sword, Knight can deal damage accurately when it is needed (the finishing stroke). 

7. **Berserker (General Male)** Axe

There is no good reason for axes. I just want to give Axes a shot. Breach + damage boosted finishing move is useful. Axe's rank 6 finishing move (double hit) is attractive. 

Equipment with AGI bonus is favored since Berserker already has fewest attacking opportunities, every hit matters.

8. **Beast Tamer (Sara)** Throwing Weapon

The reason is the same as Warrior's. And Throwing Weapon deals more damage than other 1-H ranged weapons.

Beast Tamers are much tougher than archers, so they can stand at more dangerous places.

9. **Air Dragon**

I caught it so I use it.

10. **Vartan (Canopus)** Throwing Weapon; Lighting magic; Absorb MP

Vartan is actually squashy. To allow him to attack from a safe place, ranged weapons are preferred and Throwing Weapon has the highest ATK. He can fly and he is not so fragile as archer, so shorter attack range can be tolerated.

Galvanize (melee acc up) will be used in Turn 1, and Trajectory will be used in Turn 2. 

Absorb MP: drain up enemy Cleric's MP.

##### Play

Since this stage is hard, I did some random battles to level up my team from 10 to 11 so that the archer has access to Silence.

The strategy is simple: 

0. In turn 1, melee units will be granted Truestrike + Dodge + Resilient.
1. Shutdown the boss with the archer's silence art of war / spear's rank 2 silence finishing move / air dragon's silence breath / ~~dagger's rank 2 drain MP finishing move~~ (bugged in 0.960 version). Axe's and thrown weapon's rank 2 finishing move can slow her.
2. Kill Xapan first.
3. Hold the frontline with the knight and other units having rampart aura.
4. Kill magicians, push the frontline forward and find an opportunity to kill clerics.

![Lucky to kill the first Cleric fast. Note that the front line is well controlled. (The phantom on the right of Denam is ally's.)](https://shiina18.github.io/assets/posts/images/20200711174411953_31673.jpg "Lucky to kill the first Cleric fast. Note that the front line is well controlled. (The phantom on the right of Denam is ally's.)")

![Time to kill the boss. As mentioned previously, Knight, Cleric and Spellblade are the thoughest classes so they usually survive.](https://shiina18.github.io/assets/posts/images/20200711174553811_30038.jpg "Time to kill the boss. As mentioned previously, Knight, Cleric and Spellblade are the thoughest classes so they usually survive.")

![I misplayed a lot and there is a bug on heartbreaker, so the party lost heavily. Those phantoms are really annoying without a Terror Knight.](https://shiina18.github.io/assets/posts/images/20200711174423471_184.jpg "I misplayed a lot and there is a bug on heartbreaker, so the party lost heavily. Those phantoms are really annoying without a Terror Knight.")

Heal counts: 17

Consumable counts: 7

#### Brigantys West Curtain Wall at Chapter 3 Route C

2020/8/8

- Version: 0.963a
- Target: Vartan
- Enemy: 13, including 2 Clerics. Level 14.
- Player: up to 12, but I will only use 10, which will make it much harder. Level 13.

##### Points

There is more to this battle than meets the eye.

- From version 0.963 on, tamer + monster combo has its day. The Octopuses are extremely dangerous. In version 0.963, with Empower Beast, they are able to tear apart my archer, mage and vartan by just one hit (Blue Spiral, which is even a long ranged AOE). In version 0.963a, monsters are nerfed a little, so our squashies won't be struck down by a single knock.
- 14 is a critical level: new 2-h bows, light armor, mage armor, AOE magic 2 and so on.
- Due to the Heal Clause, Heal is limited, while the boss vartan will charge to us with archers, mages and clerics left on the bank. According to the Objection Clause, we have to cross the moat and manage to kill them all.
- The terrain is obnoxious, with a large water area and high difference of height on the opposite bank. The arhcers and mages on the bank hit really hard and, with 2 clerics and nasty terrian, it is not easy work to vanquish them. Additionally, Bow's rank 2 finisher Leaden and Cudgel's rank 2 finisher Shackle make life harder.

##### Teambuilding Updates

Wade is a must, and Jump also helps a lot (jumping up 3 tiles is enough).

In hindsight, Squash should also be useful when we reach the other side of the moat.

- **Spellblade** added Ice magic

This battle might be the perfect showcase for Winter Siege.

Winter Siege has been buffed several times (and renamed since the first modification). For the first time Waterwalk is added which is proposed by me. Imagine that we use some ice spell to freeze the water and then walk on it. For this time version 0.963a, it affects multiple targets, which might result from my complain that Winter Siege is inferior to Hover Flight in most cases.

- **Berserker** double attack

##### Play

- Kill the Octopuses before they can activate any damage skill. Don't attack them offhand in the first round or two, which will only help them accumulate TP.
- Lure the melee fighters to the middle of the moat and archers to the shore. Then kill them.
- Vartans can't learn Wade, so they are not able to stay in the water. With that in mind, we can occupy the small island consisiting of 3 tiles in the midst of water and deploy our soliders in the water, so that they won't be approached by the boss.
- Cross the moat, land and slaughter. Do it as quickly as possible since we have a quota of only 12 heal and 6 consumables.

![Two enemy archers have been killed already. Our melee fighers landed safely, while the archer and the mage were killed later by the boss. (I misplayed here.) The hoplite is just too tough, and we'd better bind him and leave him alone.](https://shiina18.github.io/assets/posts/images/20200808085802835_8829.png "Two enemy archers have been killed already. Our melee fighers landed safely, while the archer and the mage were killed later by the boss. (I misplayed here.) The hoplite is just too tough, and we'd better bind him and leave him alone.")

![Stage Clear](https://shiina18.github.io/assets/posts/images/20200808085825899_31377.png "Stage Clear")

Heal counts: 11

Consumable counts: 4

To be continued...
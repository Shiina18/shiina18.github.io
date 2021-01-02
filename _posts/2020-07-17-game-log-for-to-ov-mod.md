---
title: "Game Log for Tactics Ogre LUCT One Vision Mod"
categories: Games
updated: 2021-01-02
comments: true
mathjax: false
---

I have moved some contents (including cheatcode generators) to [wiki](https://github.com/Shiina18/tactics_ogre_one_vision_mod_challenges/wiki) to reduce clutter. (2020/11/1)

[Here](https://shiina18.github.io/games/2021/01/02/to-challenges/) is the new post. (2021/1/2)

<!-- more -->

## One Vision Mod

I came across this mod one year ago when I wanted to figure out how the damage is calculated on earth, since it is really mysterious and confused me for many years. I searched in Japanese at first but failed to find any useful information. Then I tried in English and reached the calculation breakdown sheet. I noticed that the author had a mod called OV. I played with it and liked it very much. It fullfils my imagination when I first played this game years ago. So I began to propagate it in Chinese community. Now there are several people having played with this mod in China. While most are just scared away for being unable to read English.

The information for OV mod can be found [here](https://www.moddb.com/mods/one-vision1).

## Playing Log

### Self-imposed Challenges

The following clauses aim at making the game more difficult. This is called「縛りプレイ」in Japanese.

> 様々な要素からゲームを今クリアするだけなら難易度が低いゲームに対し、自主的な制限をつけることで敢えて難易度を引き上げ、やりごたえのあるゲームを自ら作り上げる、と言うのが縛りプレイの主な趣旨である。Source: [ニコニコ大百科](https://dic.nicovideo.jp/a/%E7%B8%9B%E3%82%8A%E3%83%97%E3%83%AC%E3%82%A4)

Check [here](https://github.com/Shiina18/tactics_ogre_one_vision_mod_challenges) for the latest rules. (2020/9/27)

If you are interested, you may download some saves [here](https://github.com/Shiina18/tactics_ogre_one_vision_mod_challenges) to do some challenges. (2020/9/23)

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

- **Warrior (Denam)** Spear with range 2-3

**For classes without magic, it is essential to have high attack range so that the unit can have more opportunities to make an impact on the battlefield.** To give some insight, suppose the move range + attack range = n, then the attainable area is 2n^2 + 2n + 1, ignoring terrain. In this case, move range 5 + attack range 3 = 8, attainable area = 145; while if n=5+1=6, then attainable area = 85, which is way smaller.

In order to employ class skills, melee weapons are favored. So a spear with range 2-3 is chosen.

- **Archer (General Female)** 2-H Bow

Their main attacking targets are casters and archers. Bows are favored given that Crossbows will often be blocked.

Using Bridle to mute magicians is crucial.

2-H Bows are chosen for higher attack range and atk. Archers will typically be killed by archers and magicians, so better stay in a safe place.

- **Wizard (General Male)** Dark and Ice Magic

Dark magic provides an arsenal for controlling in early game.

TP controlling is important. Players should avoid being hit by finishing moves. Ice magic Frostbite is handy for that.

- **Cleric (Donnalto)** Fist; Absorb MP

Fists are light and 1-H, and provide some AVD bonus, so are favored.

Cleric wears light armor to lower RT and to attract some attack. 

Absorb MP: You can drain alley magician's MP when needed.

- **Spellblade (Cistina)** Dagger; Air, Water Magic

This build is for controlling and supporting purposes.

Dagger is used together with Fated Circle to bind enemies. Rank 2 finishing move is also useful to shutdown magicians and to gain MP in the same time.

Air for Grace and flight, Water for healing.

Grace (melee avd up) will be used in Turn 1, and Fated Circle will be used from Turn 2.

Spellblade wears heavy armor. With HP Infusion (and Spike Skin), they can be really tough so more DEF is favored.

- **Knight (Voltare)** Sword

There is no adequate reason for swords. Other options also work.

One advantage is that sword has 2-H variant which is counted as 1-H, so Knight may use 2-H variant to maximize damage (with rank 2 finishing move or Instill Light).

**Unnessary battles should be avoided for TP controlling purpose so that the enemy can't use finishing moves or critical skills frequently.** Typically, Knights should prioritize restoring status for others rather than attacking. Attacking leads to TP accumulation for the target and a counterhit from him which results in HP reduction for the attacker. With sword, Knight can deal damage accurately when it is needed (the finishing stroke). 

- **Berserker (General Male)** Axe

There is no good reason for axes. I just want to give Axes a shot. Breach + damage boosted finishing move is useful. Axe's rank 6 finishing move (double hit) is attractive. 

Equipment with AGI bonus is favored since Berserker already has fewest attacking opportunities, every hit matters.

- **Beast Tamer (Sara)** Throwing Weapon

The reason is the same as Warrior's. And Throwing Weapon deals more damage than other 1-H ranged weapons.

Beast Tamers are much tougher than archers, so they can stand at more dangerous places.

Another import reason for using throwing weapons is that, ideally tamers should use one skill every turn, and using a ranged weapon allows them to find a better position for both attacking and utilizing skills in one turn. (2020/9/14)

- **Air Dragon**

I caught it so I use it.

- **Vartan (Canopus)** Throwing Weapon; Lighting magic; Absorb MP

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

#### Phidoch South Curtain Wall at Chapter 3 Route C

2020/8/21

- Version: 0.963b beta (not released formally, with some archer and mage set modification)
- Target: Mage
- Enemy: 13 + 10, including 2 Clerics (and possibly more Clerics from reinforcement). Level 16.
- Player: 12. Level 15.

##### Teambuilding Updates

This time we have fresh blood in our crew. 

- **Blade Knight (Hobyrim)**

First time to use blade knight. I will talk more about it in the future.

- **Warlock (Cerya)** Dagger variant (Spellstrike), and equipment that maximizes MND.
    - Air: AOE bind
    - Water: AOE heal; Leaden + Slow + RT delay, very useful to some bosses (e.g. twelve heavenly)
    - Fire/Earth/Ice: shutdown. I use Fire this time since it fits Cerya and turn-based status (shackle and petrify) is easier to track than RT-based (stop) so I can know when it will expire.
    - Lightning: Useful to some bosses, their turn will not come forever.
    - Dark: Similar with Terror Knight. Drain MP, very useful to mage bosses. Charm, useful to units full of TP.
    - Light: Never used.

Carries Water, Fire and Dark this time.

Warlock is one of the best classes in the game. Shutdown status is all OP imo. This build is dedicated to inflicting shutdown status. What's more, **warlock in this build doesn't need any ranked skills**.

Spellstrike is used in Turn 1. And with the help of Instill Mind, she can shut down enemies with nearly 100% acc every turn consistently.

The regular 10 will remain the same and these 2 will only be used when a party of 12 members is called for.

- **Archer**

Has rank 4 bow finisher (sleep) now, which is OP (and this is one of the reasons I prefer bows than crossbows).

Has access to stun-bringer.

- **Knight**

Now uses a shield that inflicts stun.

In hindsight, my spellblade should bring Fire magic to counter Weaken...

##### Points

Though there are 23 enemies in total, it's quite easy to vanquish them all, since (1) we have more useful tools and (2) we have one of the best classes in our team now.

- Lv 16 is a critical level for new weapons and shields.
- There are no terror knights, so Phalanx is very effective.

##### Play

- Spam stun, and trap and delay enemies so that there are fewer active foes in the battlefield and they take fewer effective turns.
- In the first few turns, warlock is tasked with shackling appropriate units (considering there are 2 knights, shutdown isn't very reliable).
- Find an opportunity to drain up boss' MP and then keeps her MP bar clean.
- Kill clerics via applying silence or absorbing their MP.

![Warlock has a chance to drain up boss' MP. Enemy knights are trapped. The wingedman cleric is sleeping thanks to bow's finisher.](https://shiina18.github.io/assets/posts/images/20200822004148188_4927.png "Warlock has a chance to drain up boss' MP. Enemy knights are trapped. The wingedman cleric is sleeping thanks to bow's finisher.")

![Keep cleric's mp empty or silence him. I misplayed so Hob is incap in an early stage.](https://shiina18.github.io/assets/posts/images/20200822004314043_28679.png "Keep cleric's mp empty or silence him. I misplayed so Hob is incap in an early stage.")

![There are 4 clerics (2 wingedmen) in enemy side in the same time! And one of them has been killed, and the one pointed by the cursor gets trapped. The phantom protects our casters from being attacked by the dragoon in the right hand side. In the left hand side, the warrior can't move anywhere and the dragoon is bound by our spellblade.](https://shiina18.github.io/assets/posts/images/20200822004451249_19571.png "There are 4 clerics (2 wingedmen) in enemy side in the same time! And one of them has been killed, and the one pointed by the cursor gets trapped. The phantom protects our casters from being attacked by the dragoon in the right hand side. In the left hand side, the warrior can't move anywhere and the dragoon is bound by our spellblade.")

Heal counts: 20

Consumable counts: 6

#### Bahanna Highlands at Chapter 4 Route C

2020/8/29

0.963c

Enemies have higher tier gears, level and projective spell 3. Additonally, all skill ranks of enemies are raised to rank 4 by myself.

Watch the video [here](https://www.acfun.cn/v/ac17664467). Many misplays due to the fact that I forgot to check out the action orders multiple times.

#### Hagia Banhamuba at Chapter 4 Route C

Watch the video [here](https://www.acfun.cn/v/ac17664467_2). It's a slightly different team, and I play better this time. You may see how carefully the dragoons are being treated and I pass my turns doing nothing sometimes just because I can't do anything that is able to bring advantages that turn.

#### Challenge: Knight General in the Forest

2020/9/1

Thank severusia for sharing the save. 

I build a team with her characters and vanquish the knight general (lv. 33) in the forest with a team of lv. 24-27 at the first attempt.

Watch the video [here](https://www.acfun.cn/v/ac17706243) on AcFun or [here](https://www.youtube.com/watch?v=U2Q3n5HnjwE&feature=youtu.be) on YouTube. The video partly shows the reason why I have to impose so many restrictions as written previously to make game worth playing.

Tbh, this battle is way too easy partly because it hasn't been reworked yet. 

> Team
> 
> - defensive core: cleric, knight, white knight (can be replaced with knight), lord (can be replaced)
> - offensive core: berserker, terror knight, blade knight (can be replaced with swordmaster), vartan
> - controling core: warlock (rt reset), spellblade (sleeping fan + guaranteed hit), rogue (sleeping blowgun + guaranteed hit)
> - burden: dragoon (sadly useless in this battle) 
> 
> classes can be replaced arbitrarily except cleric, knight and warlock, which are the best classes.

Some strategies I came up with beforehand. Sadly the enemy is so weak that I even didn't have a chance to apply them. The strategy is very general and can be applied using generic classes and generic characters without grinding skill ranks and gears. 

- They don't have shadwobreak/squash, Phanlanx is god.
- High rank rampart aura is god.
- Use silence and MP drain to dispose of healers. In high level, MP drain works very well since maximum MP is much higher.
- Use dragoon to deal with dragons.
- Status might be not effective since they have many healers.
- We have level disadvantage, so the base damage overhead is typically zero. So we 'd better to choose strategies relied on extra damage rahter than base damage. 
- Since they have tons of healers, we should rely on burst damage to finish them one by one. TK's preserved fearful impact +shadowbreak is something I used to use frequently.
- Inflict Stun (hammer +guaranteed hit) to Full Ward enemies, then silence/slow/leaden.
- Prevent enemies from using finishers. (ice magic, art of war, drain power, and some finishers to deal with TP)
- Use flight (air magic) or winter siege (ice magic) to deal with rampart aura.
- ...

In fact, the point is, to lure two dragons throwing, which costs very high RT penalty, then reset their RT forever. So in fact, the match is over when my warlock takes his second turn at around 5:00 of the video.

```
due to [lanchester laws](https://en.wikipedia.org/wiki/Lanchester%27s_laws) which can be applied in this game, shutting down a unit for 2 or 3 turns is invaluable
even if the status is restored immediately later, you can choose the target deliberately to pass at least one of his turn
then you make one move to pass two moves of enemies
that's invaluable in turn-based games
```

To be continued...

See [Tactics Ogre One Vision Mod Challenges](https://github.com/Shiina18/tactics_ogre_one_vision_mod_challenges) for further updates. (2020/10/16)
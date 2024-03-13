class Constants:
  SkillPenaltyTable = {
     0: 30, 
     1: 40, 
     2: 50, 
     3: 58, 
     4: 64, 
     5: 70, 
     6: 76, 
     7: 81, 
     8: 86, 
     9: 90, 
    10: 94, 
    11: 97, 
    12: 100, 
    13: 102, 
    14: 105, 
    15: 107, 
    16: 110}
  LevelPenaltyTable = {
     1:  1, 
     2:  3, 
     3:  5, 
     4:  8, 
     5: 11, 
     6: 14, 
     7: 18}
  StatusResistBonusTable = {
    "drainStamina": 0,
    "disease": 2,
    "irritated": 3,
    "nausea": 4,
    "slow": 4,
    "afraid": 5,
    "poisoned": 6,
    "silenced": 7,
    "hex": 8,
    "enthrall": 9,
    "insanity": 10,
    "blind": 12,
    "turncoat": 14,
    "web": 16,
    "sleep": 20,
    "paralyzed": 18,
    "unconscious": 22,
    "death": 24
  }
  EffectTypeMultipliers = {
    "spell":   1.0, 
    "artifact":0.9, 
    "thrown":  0.8}
  FullCasters = {"mage", "priest", "alchemist", "psionic", "bishop"}
  HybridCasters = {"samurai", "valkyrie", "lord", "ranger", "ninja", "monk"}
  Spellbooks = {"wizardry", "divinity", "alchemy", "psionics"}
  Elements = {"fire", "water", "air", "earth", "mental", "divine"}

class Defaults:
  BookSkills = {book:0 for book in Constants.Spellbooks}
  ElementSkills = {element:0 for element in Constants.Elements}
  Resistances = {element:0 for element in Constants.Elements}

def casterLevel(profession: str, level: int):
  if profession in Constants.FullCasters:
    return level
  elif profession in Constants.HybridCasters:
    return level-4
  else:
    return 0

def validateOptionArgument(arg, validSet: set, thingType: str = ""):
  if arg not in validSet:
    raise ValueError(
      arg + " is not a valid " + thingType + " option. " + 
      "Known options are " + str(validSet))

class Spell:
  def __init__(self, 
      name: str, 
      book: str, 
      element: str, 
      level: int, 
      baseCost: int,
      statusList: list = []):
    validateOptionArgument(book, Constants.Spellbooks, "spellbook")
    validateOptionArgument(element, Constants.Elements, "element")
    self.name = name
    self.book = book
    self.element = element
    self.level = level
    self.baseCost = baseCost
    skillDifficultyIndex = int(baseCost/2) + int(level)
    self.skillDifficulty = Constants.SkillPenaltyTable[skillDifficultyIndex]
    self.levelDifficulty = Constants.LevelPenaltyTable[level]
    self.statusList = statusList

class SkillSet:
  def __init__(self, skillValues: dict):
    self.skillValues = skillValues

class Caster:
  def __init__(self, 
      profession: str, 
      level: int, 
      name: str               = "Caster", 
      bookSkills:    SkillSet = None, 
      elementSkills: SkillSet = None,
      powerCastSkill: int = 0):
    self.name = name
    self.profession = profession
    self.level = level
    self.bookSkills = Defaults.BookSkills
    self.elementSkills = Defaults.ElementSkills
    self.casterLevel = casterLevel(profession, level)
    self.powerCastSkill = powerCastSkill
    if bookSkills is not None:
      for book in bookSkills.keys():
        validateOptionArgument(book, Constants.Spellbooks, "spellbook")
        self.bookSkills[book] = bookSkills[book]
    if elementSkills is not None:
      for element in elementSkills:
        validateOptionArgument(element, Constants.Elements, "element")
        self.elementSkills[element] = elementSkills[element]
  def weightedSkill(self, book: str, element: str):
    return int((self.bookSkills[book] + 4*self.elementSkills[element])/5)

class Enemy:
  def __init__(self, 
      level: int, 
      name: str               = "Enemy", 
      resistances:   SkillSet = None):
    self.name = name
    self.level = level
    self.resistances = Defaults.Resistances
    if resistances is not None:
      for element in resistances.keys():
        validateOptionArgument(element, Constants.Elements, "element")
        self.resistances[element] = resistances[element]

class CastParams:
  def __init__(self, 
      powerLevel: int, 
      effectType: str = "spell", 
      unidentifiedItem: bool = False):
    self.powerLevel = powerLevel
    self.effectType = effectType
    self.unidentifiedItem = unidentifiedItem

def skillFailChance(spell: Spell, caster: Caster, params: CastParams):
  castSkillDifficulty = int(spell.skillDifficulty * params.powerLevel/7)
  weightedCasterSkill = caster.weightedSkill(spell.book, spell.element)
  effectMultiplier = Constants.EffectTypeMultipliers[params.effectType]
  relativeSkill = weightedCasterSkill / castSkillDifficulty
  baseSkillFailChance = int(70 * (1 - relativeSkill))
  itemOffset = 30*int(params.unidentifiedItem)
  return int(baseSkillFailChance * effectMultiplier) + itemOffset

def levelFailChance(spell: Spell, caster: Caster, params: CastParams):
  levelDeficit = spell.levelDifficulty - caster.casterLevel
  baseFailChance = levelDeficit + params.powerLevel - 1
  return int(baseFailChance*spell.level)

def castOutcomeChances(spell: Spell, caster: Caster, params: CastParams):
  skillFail = max(skillFailChance(spell, caster, params), 0)
  levelFail = max(levelFailChance(spell, caster, params), 0)
  overallFail = skillFail + levelFail
  backfireChance = int(overallFail / 3) if overallFail >= 15 else 0
  return {
    "skillFail": skillFail, 
    "levelFail": levelFail, 
    "overallFail": overallFail, 
    "backfire": backfireChance, 
    "fizzle": overallFail - backfireChance, 
    "success": 100 - overallFail}

def resistChances(spell: Spell, enemy: Enemy, caster: Caster, params: CastParams):
  spellBaseStrength = int(spell.level + int(spell.baseCost/2) / 2)
  castStrength = spellBaseStrength + params.powerLevel + int(caster.casterLevel/2)
  powerCastFactor = (100 + int((1 + int(caster.powerCastSkill/4))/2))
  resistDelta = (enemy.level - int(castStrength*powerCastFactor/100))*3
  resistPct = enemy.resistances[spell.element] + resistDelta
  statusResist = {status: min(max(resistPct + Constants.StatusResistBonusTable[status],5),95) for status in spell.statusList}
  return {
    "baseResist": enemy.resistances[spell.element],
    "baseSpellStrength": spellBaseStrength,
    "castStrength": castStrength,
    "powerCastFactor": powerCastFactor,
    "resistDelta": resistDelta,
    "resistPct": min(max(resistPct,5),95),
    "minDmgResist": min(max(resistPct - int(resistPct/2),0),100),
    "maxDmgResist": min(max(resistPct + int(resistPct/2),0),100),
    "statusResist": statusResist}

def main():
  theCaster = Caster(
    profession = "samurai", 
    level = 5, 
    bookSkills = {"wizardry":3},
    elementSkills = {"fire":0})
  theSpell = Spell(
    name = "Terror",
    level = 1,
    book = "wizardry",
    element = "mental", 
    baseCost = 3,
    statusList = ["afraid"])
  theParams = CastParams(
    powerLevel = 1)
  theEnemy = Enemy(
    level = 8,
    resistances = {"fire":25, "water":80, "earth":60, "air":70})
  outcomeProbs = castOutcomeChances(theSpell, theCaster, theParams)  
  resistProb = resistChances(theSpell, theEnemy, theCaster, theParams)
  print(theCaster.name,"is a level",theCaster.level,theCaster.profession,"which gives them a caster level of",theCaster.casterLevel,"\n")  
  print(theCaster.name + "'s Book skills are:")
  for key in theCaster.bookSkills:
    print("  ",str(key) + ":",theCaster.bookSkills[key])
  print("")
  print(theCaster.name + "'s Element skills are:")
  for key in theCaster.elementSkills:
    print("  ",str(key) + ":",theCaster.elementSkills[key])
  print ("")
  print("The spell being cast is",theSpell.name,"which has the following properties:")
  print("  Book:",theSpell.book)
  print("  Element:",theSpell.element)
  print("  Level:",theSpell.level)
  print("  Base Cost:",theSpell.baseCost)
  print("  Weighted skill to Reliably Cast at Base Power:",int(theSpell.skillDifficulty/7))
  print("  Weighted skill to Reliably Cast at Max Power:",theSpell.skillDifficulty)
  print("  Caster Level to Reliably Cast at Base Power:",theSpell.levelDifficulty)
  print("")
  print("For",theSpell.element,"spells in the",theSpell.book,"book,",theCaster.name,"has a weighted skill level of",theCaster.weightedSkill(theSpell.book, theSpell.element),"\n")
  print(theSpell.name,"is being cast at power level",theParams.powerLevel)
  print("")  
  print("This gives the following outcome probabilities:")
  print("  Success:",outcomeProbs["success"],"%")
  print("  Overall Failure:",outcomeProbs["overallFail"],"%")
  print("    Breakdown by Reason:")
  print("      Skill Based:",outcomeProbs["skillFail"],"%")
  print("      Level Based:",outcomeProbs["levelFail"],"%")
  print("    Breakdown by Outcome:")
  print("      Backfire:",outcomeProbs["backfire"],"%")
  print("      Fizzle:",outcomeProbs["fizzle"],"%")
  print("")
  print("On a success, the enemy's resistance level would be:",resistProb["resistPct"],"%, based on")
  print("  Base Resist:",resistProb["baseResist"])
  print("  Resist Modifier:",resistProb["resistDelta"])
  print("    Base Spell Strength:",resistProb["baseSpellStrength"])
  print("    Cast Power:",resistProb["castStrength"])
  print("    Power Cast Multiplier:",resistProb["powerCastFactor"])
  print("  Damage Reduction Range:","["+str(resistProb["minDmgResist"])+","+str(resistProb["maxDmgResist"])+"]")
  print("  Status Resistance Chances:")
  if not resistProb["statusResist"]: 
    print("    N/A")
  else:
    for status in resistProb["statusResist"].keys():
      print("    " +str(status)+":", resistProb["statusResist"][status])

if __name__ == "__main__":
  main()
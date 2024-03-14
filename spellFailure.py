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
    self.skillDifficulty = self.getSkillDifficulty()
    self.levelDifficulty = self.getLevelDifficulty()
    self.statusList = statusList
    self.baseStrength = self.getBaseStrength()
  def getSkillDifficulty(self):
    index = int(self.baseCost/2) + int(self.level)
    return Constants.SkillPenaltyTable[index]
  def getLevelDifficulty(self):
    return Constants.LevelPenaltyTable[self.level]
  def getBaseStrength(self):
    return int(self.level + int(self.baseCost/2) / 2)
  def __repr__(self):
    return f"""
    Name: {self.name}
    School: {self.book}
    Realm: {self.element}
    Level: {self.level}
    Cost/Level: {self.baseCost}
    Statuses: {self.statusList}
    Weighted skill to Reliably Cast at Base Power: {int(self.skillDifficulty/7)}
    Weighted skill to Reliably Cast at Max Power: {int(self.skillDifficulty)}
    Caster level to Reliably Cast at Max Power: {int(self.levelDifficulty)}
    Base Power to Overcome Resistance: {int(self.baseStrength)}
    """

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
  def __repr__(self):
    bookSkills = "\n".join(
      [f"      {book}: {self.bookSkills[book]}" for book in self.bookSkills])
    elementSkills = "\n".join(
      [f"      {element}: {self.elementSkills[element]}" for element in self.elementSkills])
    return f"""
    Name: {self.name}
    Class: {self.profession}
    Level: {self.level}
    Caster Level: {self.casterLevel}
    School Skills:\n{bookSkills}
    Element Skills:\n{elementSkills}
    """

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
  def __repr__(self):
    resistances = "\n".join([f"    {element}: {self.resistances[element]}" for element in self.resistances])
    return f"""
    Type/Name: {self.name}
    Level: {self.level}
    Resistances:\n{resistances}
    """

  
class CastParams:
  def __init__(self, 
      powerLevel: int, 
      effectType: str = "spell", 
      unidentifiedItem: bool = False):
    self.powerLevel = powerLevel
    self.effectType = effectType
    self.unidentifiedItem = unidentifiedItem

    
class SpellOutcomeChances:
  def __init__(self,
      skillFailChance: int,
      levelFailChance: int,
      overallFailChance: int,
      backfireChance: int,
      fizzleChance: int,
      successChance: int):
    self.skillFail = skillFailChance
    self.levelFail = levelFailChance
    self.overallFail = overallFailChance
    self.backfire = backfireChance
    self.fizzle = fizzleChance
    self.success = successChance
  def __repr__(self):
    return f"""
    Success: {self.success}%
    Fail: {self.overallFail}%
      By Reason:
        Skill: {self.skillFail}%
        Level: {self.levelFail}%
      By Subtype:
        Backfire: {self.backfire}%
        Fizzle: {self.fizzle}%
    """

  
class SpellInstance:
  def __init__(self,
      caster: Caster,
      spell: Spell,
      params: CastParams):
    self.caster = caster
    self.spell = spell
    self.params = params
    self.weightedSkill = self.getWeightedSkill()
    self.castSkillDifficulty = self.getCastSkillDifficulty()
    self.skillFailChance = self.getSkillFailChance()
    self.levelFailChance = self.getLevelFailChance()
    self.overallFailChance = self.getOverallFailChance()
    self.backfireChance = self.getBackfireChance()
    self.castStrength = self.getCastStrength()
    self.powerCastFactor = self.getPowerCastFactor()
    self.referenceEnemyLevel = self.getReferenceEnemyLevel()
  def getWeightedSkill(self):
    bookSkill = self.caster.bookSkills[self.spell.book]
    elementSkill = self.caster.elementSkills[self.spell.element]
    return int((bookSkill + 4*elementSkill)/5)
  def getCastSkillDifficulty(self):
    return int(self.spell.skillDifficulty * self.params.powerLevel/7)
  def getSkillFailChance(self):
    effectMultiplier = Constants.EffectTypeMultipliers[self.params.effectType]
    relativeSkill = self.weightedSkill / self.castSkillDifficulty
    baseSkillFailChance = int(70 * (1 - relativeSkill))
    itemOffset = 30*int(self.params.unidentifiedItem)
    return max(int(baseSkillFailChance * effectMultiplier) + itemOffset,0)
  def getLevelFailChance(self):
    levelDeficit = self.spell.levelDifficulty - self.caster.casterLevel
    baseFailChance = levelDeficit + self.params.powerLevel - 1
    return max(int(baseFailChance*self.spell.level),0)
  def getOverallFailChance(self):
    return min(self.skillFailChance + self.levelFailChance, 100)
  def getBackfireChance(self):
    return int(self.overallFailChance / 3) if self.overallFailChance >= 15 else 0
  def getCastStrength(self):
    return self.spell.baseStrength + self.params.powerLevel + int(self.caster.casterLevel/2)
  def getPowerCastFactor(self):
    return (100 + int((1 + int(self.caster.powerCastSkill/4))/2))
  def getReferenceEnemyLevel(self):
    return int(self.castStrength*self.powerCastFactor/100)
  def castOutcomeChances(self):
    fizzle = max(self.overallFailChance - self.backfireChance,0)
    success = 100 - self.overallFailChance
    return SpellOutcomeChances(
      self.skillFailChance,
      self.levelFailChance,
      self.overallFailChance,
      self.backfireChance,
      fizzle,
      success)
  def __repr__(self):
    return f"""
    Power Level: {self.params.powerLevel}
    Source: {self.params.effectType}
      Unidentified Item?: {self.params.unidentifiedItem}
    Weighted Caster Skill: {self.weightedSkill}
    Skill Difficulty at Level: {self.castSkillDifficulty}
    """
    

class SpellImpact:
  def __init__(self, spellInstance: SpellInstance, targets: list[Enemy]):
    self.spellReferenceLevel = spellInstance.referenceEnemyLevel
    self.element = spellInstance.spell.element
    self.targets = targets
    self.statuses = spellInstance.spell.statusList
    self.baseResists = [
      enemy.resistances[self.element]
      for enemy in self.targets]
    self.resistPcts = [
      self.resistPct(enemy)
      for enemy in self.targets]
    self.damageProfiles = [
      SpellImpact.damageEfficiency(resistPct)
      for resistPct in self.resistPcts]
    self.statusProfiles = [
      {status: SpellImpact.statusResistPct(resistPct, status)
       for status in self.statuses}
        for resistPct in self.resistPcts]
  def resistPct(self, enemy):
    resistDelta = (enemy.level - self.spellReferenceLevel)*3
    resistPct = enemy.resistances[self.element] + resistDelta
    return resistPct
  def damageEfficiency(resistPct):
    maxEfficiency = max(100 - max(resistPct - int(resistPct/2), 0), 0)
    minEfficiency = max(100 - max(resistPct + int(resistPct/2), 0), 0)
    return (minEfficiency, maxEfficiency)
  def statusResistPct(resistPct, status):
    return 100 - min(max(resistPct + Constants.StatusResistBonusTable[status],5),95)
  def __repr__(self):
    damageProfileString = "\n".join([
      f"  {self.targets[i].name} {i}: {self.damageProfiles[i][0]}-{self.damageProfiles[i][1]}%"
      for i in range(len(self.targets))])
    statusProfileString = "\n".join([
      f"  {self.targets[i].name} {i}: {self.statusProfiles[i]}"
      for i in range(len(self.targets))])
    return f"""
    Damage Profiles:
    {damageProfileString}
    Status Profiles:
    {statusProfileString}
    """

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
  theInstance = SpellInstance(theCaster, theSpell, theParams)
  outcomeProbs = theInstance.castOutcomeChances()  
  resistProbs = SpellImpact(theInstance, [theEnemy])
  print("CASTER")
  print(theCaster)
  print("SPELL")
  print(theSpell)
  print("SPELL INSTANCE")
  print(theInstance)
  print("CASTING OUTCOMES")  
  print(outcomeProbs)
  print("TARGETS")
  print(theEnemy)
  print("EFFICIENCIES")
  print(resistProbs)

if __name__ == "__main__":
  main()

"""Builds recipes.json for the Ninja Luxe Café Pro recipe site.

Every recipe is written as exact steps for the Ninja Luxe Café Pro (ES701).
Ninja's own recipes are marked source.kind == "ninja" (built-in defaults).
Outside recipes are source.kind == "web", rewritten in our own words with a link to the original.

Run:  python3 build_recipes.py   -> writes recipes.json next to this file and runs the duplicate check.
To add a recipe: append an R(...) call in the right category block. The duplicate check will refuse
repeated ids, repeated names, and recipes whose drink "signature" matches an existing one.
"""
import json, re, sys, pathlib

CATEGORIES = [
    ("espresso",     "Espresso",      "Double shots and the classic café milk drinks."),
    ("ristretto",    "Ristretto",     "Short, syrupy, sweeter shots and the drinks built on them."),
    ("lungo",        "Lungo",         "Long, gentle shots for a bigger, softer cup."),
    ("americano",    "Americano",     "Espresso stretched with water, hot or iced."),
    ("cold-pressed", "Cold Pressed",  "Smooth espresso brewed cool, made for iced drinks."),
    ("classic",      "Classic Coffee","Balanced drip-style coffee and the drinks built on it."),
    ("rich",         "Rich Coffee",   "Concentrated, bolder coffee that stands up to milk and spirits."),
    ("over-ice",     "Over Ice",      "Hot coffee brewed strong to pour straight over ice."),
    ("cold-brew",    "Cold Brew",     "Low-temperature brewed coffee, smooth and mellow."),
    ("hot-water",    "Hot Water",     "Tea, matcha and other drinks from the hot water spout."),
]

NINJA_ES601 = "https://support.ninjakitchen.com/hc/article_attachments/14670435097116"
NINJA_UK = "https://support.ninjakitchen.co.uk/hc/article_attachments/15646786803868"

# ---------- step helpers (Luxe Café Pro controls) ----------

def espresso_steps(basket, style, cup, before=None, cup_prep=None):
    s = []
    if before: s += before
    s.append(f"Fit the {basket} basket into the portafilter, put the dosing funnel on and set it in the grinding cradle.")
    label = style
    if basket == "Luxe" and style == "ESPRESSO":
        label = "ESPRESSO (the Luxe basket makes it a quad shot)"
    s.append(f"Turn the center dial to {label}.")
    s.append("Turn the grind dial to the number Barista Assist recommends, then press START GRIND. The built-in scale doses by weight.")
    s.append("Pull the tamping lever down firmly twice, then lift off the funnel.")
    s.append("Lock the portafilter into the brew head.")
    if cup_prep: s.append(cup_prep)
    s.append(f"Place {cup} under the spout and press START BREW.")
    return s

def coffee_steps(style, size, cup, cup_prep=None, grounds_extra=None):
    s = ["Fit the Luxe basket into the portafilter, put the dosing funnel on and set it in the grinding cradle.",
         f"Turn the center dial to {style} and press SIZE until {size} oz lights up.",
         "Turn the grind dial to the number Barista Assist recommends, then press START GRIND."]
    if size >= 16:
        s.append("Pull the tamping lever down firmly twice, then lift off the funnel.")
    else:
        s.append("Give the portafilter a gentle shake to level the grounds, then lift off the funnel.")
    if grounds_extra: s.append(grounds_extra)
    s.append("Lock the portafilter into the brew head.")
    if cup_prep: s.append(cup_prep)
    s.append(f"Place {cup} under the spout and press START BREW.")
    return s

def froth_steps(fill, preset, milk_type="DAIRY", extra=None):
    add = f", then add {extra}" if extra else ""
    return [f"Pour {fill} into the milk jug{add}. Set the jug on the frothing platform with the whisk inside.",
            f"Press MILK TYPE until {milk_type} lights up, turn the froth dial to {preset} and press START FROTH."]

def hot_water_steps(cup, size, temp):
    return [f"Place {cup} under the hot water spout.",
            f"Press HOT WATER, set the temperature to {temp} and the size to {size}, then press START."]

RECIPES = []

def R(id, name, cat, src, serve, milk, effort, mins, makes, glass, ingredients, settings, steps,
      tips=None, note=None, sub=None, alcohol=False, flavor=None, rating=None):
    RECIPES.append(dict(
        id=id, name=name, category=cat,
        source=dict(kind=src[0], site=src[1], url=src[2]),
        rating=rating, serve=serve, milk=milk, effort=effort, alcohol=alcohol,
        minutes=mins, makes=makes, glass=glass,
        ingredients=ingredients, settings=settings, steps=steps,
        tips=tips or [], adaptation=note, subRecipes=sub or [], flavor=flavor or []))

def S(basket=None, style=None, size=None, froth=None, milkType=None, temp=None, hotWater=None):
    return {k: v for k, v in dict(basket=basket, style=style, size=size, froth=froth,
                                     milkType=milkType, temp=temp, hotWater=hotWater).items() if v}

NINJA = lambda url=NINJA_ES601: ("ninja", "Ninja Luxe Café recipe guide", url)
NINJA_WEB = lambda url: ("ninja", "Ninja (sharkninja.com)", url)
NINJA_UKG = ("ninja", "Ninja Luxe Café recipe guide (UK)", NINJA_UK)

# ======================================================================
# ESPRESSO
# ======================================================================
R("espresso-shot", "Espresso Shot", "espresso", NINJA_UKG, "hot", False, "quick", 2, "1 double shot", "Espresso cup",
  ["Fresh whole coffee beans"],
  S("Double", "ESPRESSO"),
  espresso_steps("Double", "ESPRESSO", "a warm espresso cup"),
  tips=["Use the Single basket for a single shot or the Luxe basket for a quad.",
        "New beans can take 2 or 3 shots before Barista Assist settles on the right grind."],
  flavor=["bold"])

R("latte", "Latte", "espresso", NINJA_UKG, "hot", True, "quick", 4, "1 latte", "Large mug",
  ["Fresh whole coffee beans", "Milk of your choice, up to the LATTE line on the jug"],
  S("Double", "ESPRESSO", froth="THIN FROTH", milkType="DAIRY or PLANT-BASED"),
  espresso_steps("Double", "ESPRESSO", "a large mug") +
  froth_steps("milk up to the LATTE line", "THIN FROTH", "DAIRY (or PLANT-BASED)") +
  ["Pour the milk into the espresso, finishing with a thin layer of foam."],
  tips=["You can start frothing while the shot brews: set the froth options during brewing and press START FROTH, and it begins as soon as the shot ends."],
  flavor=["creamy", "mellow"])

R("cappuccino", "Cappuccino", "espresso", NINJA_UKG, "hot", True, "quick", 4, "1 cappuccino", "Cappuccino cup",
  ["Fresh whole coffee beans", "Milk of your choice, up to the CAPPUCCINO line on the jug", "Cocoa powder, for dusting"],
  S("Double", "ESPRESSO", froth="THICK FROTH", milkType="DAIRY or PLANT-BASED"),
  espresso_steps("Double", "ESPRESSO", "a cappuccino cup") +
  froth_steps("milk up to the CAPPUCCINO line", "THICK FROTH", "DAIRY (or PLANT-BASED)") +
  ["Spoon the thick foam over the espresso, then dust with cocoa powder."],
  flavor=["creamy", "airy"])

R("flat-white", "Flat White", "espresso", NINJA(), "hot", True, "quick", 3, "6.5 oz", "8 oz cup",
  ["Double shot of espresso", "5 oz whole milk, chilled"],
  S("Double", "ESPRESSO", froth="THIN FROTH", milkType="DAIRY"),
  espresso_steps("Double", "ESPRESSO", "an 8 oz cup") +
  froth_steps("5 oz cold whole milk", "THIN FROTH") +
  ["Pour the silky milk into the espresso in one steady stream."],
  flavor=["velvety", "bold"])

R("macchiato", "Macchiato", "espresso", NINJA_UKG, "hot", True, "quick", 3, "1 macchiato", "Espresso cup",
  ["Fresh whole coffee beans", "Milk up to the minimum line on the jug"],
  S("Double", "ESPRESSO", froth="THICK FROTH", milkType="DAIRY"),
  espresso_steps("Double", "ESPRESSO", "an espresso cup") +
  froth_steps("milk up to the minimum fill line", "THICK FROTH") +
  ["Spoon just the foam on top of the espresso to 'mark' it."],
  flavor=["bold"])

R("cortado", "Cortado", "espresso", NINJA_UKG, "hot", True, "quick", 3, "1 cortado", "Small glass",
  ["Fresh whole coffee beans", "Milk up to the minimum line on the jug"],
  S("Double", "ESPRESSO", froth="THIN FROTH", milkType="DAIRY"),
  espresso_steps("Double", "ESPRESSO", "a small glass") +
  froth_steps("milk up to the minimum fill line", "THIN FROTH") +
  ["Pour the milk over the espresso so it's roughly equal parts coffee and milk."],
  tips=["Use the Single basket for a smaller, gentler cortado."],
  flavor=["balanced"])

R("vanilla-cappuccino", "Vanilla Cappuccino", "espresso", NINJA(), "hot", True, "quick", 3, "6.5 oz", "8 oz cup",
  ["Double shot of espresso", "1 tbsp vanilla syrup", "5 oz whole milk, chilled"],
  S("Double", "ESPRESSO", froth="THICK FROTH", milkType="DAIRY"),
  espresso_steps("Double", "ESPRESSO", "the cup", cup_prep="Add the vanilla syrup to an 8 oz cup.") +
  froth_steps("5 oz cold whole milk", "THICK FROTH") +
  ["Pour the frothed milk over the espresso."],
  flavor=["sweet", "vanilla"])

R("caramel-macchiato", "Caramel Macchiato", "espresso", NINJA(), "hot", True, "quick", 3, "3.5 oz", "6 oz cup",
  ["Double shot of espresso", "1½ tsp caramel syrup, plus extra to drizzle", "2 oz whole milk, chilled"],
  S("Double", "ESPRESSO", froth="THICK FROTH", milkType="DAIRY"),
  espresso_steps("Double", "ESPRESSO", "the cup", cup_prep="Add the caramel syrup to a 6 oz cup.") +
  froth_steps("2 oz cold whole milk", "THICK FROTH") +
  ["Pour the frothed milk over the espresso and finish with a caramel drizzle."],
  tips=["Make it iced: choose COLD-PRESSED, froth with COLD FOAM, and brew over ice."],
  flavor=["sweet", "caramel"])

R("cinnamon-honey-latte", "Cinnamon Latte with Honey", "espresso", NINJA(), "hot", True, "quick", 4, "9.5 oz", "12 oz cup",
  ["Double shot of espresso", "½ tsp ground cinnamon, plus extra to dust", "2 tsp honey", "8 oz whole milk, chilled"],
  S("Double", "ESPRESSO", froth="THIN FROTH", milkType="DAIRY"),
  ["Fit the Double basket into the portafilter, put the dosing funnel on and set it in the grinding cradle.",
   "Turn the center dial to ESPRESSO.",
   "Turn the grind dial to the number Barista Assist recommends, then press START GRIND.",
   "Sprinkle the ½ tsp cinnamon over the grounds.",
   "Pull the tamping lever down firmly twice, then lift off the funnel.",
   "Lock the portafilter into the brew head.",
   "Add the honey to a 12 oz cup, place it under the spout and press START BREW.",
   "Stir to melt the honey into the espresso."] +
  froth_steps("8 oz cold whole milk", "THIN FROTH") +
  ["Pour the milk into the cup and dust with a little cinnamon."],
  flavor=["warm spice", "honey"])

R("classic-mocha", "Classic Mocha with Chocolate Froth", "espresso", NINJA_UKG, "hot", True, "quick", 4, "1 mocha", "Large mug",
  ["Fresh whole coffee beans", "2 tbsp hot chocolate mix", "Milk up to the CAPPUCCINO line on the jug"],
  S("Double", "ESPRESSO", froth="THICK FROTH", milkType="DAIRY"),
  espresso_steps("Double", "ESPRESSO", "a large mug") +
  froth_steps("milk up to the CAPPUCCINO line", "THICK FROTH", extra="the hot chocolate mix") +
  ["Pour the chocolate froth over the espresso."],
  flavor=["chocolate"])

R("chai-latte-espresso", "Chai Latte with Espresso", "espresso", NINJA_UKG, "hot", True, "quick", 4, "1 latte", "Large mug",
  ["Fresh whole coffee beans", "3 tsp chai powder", "Milk up to the LATTE line on the jug"],
  S("Single", "ESPRESSO", froth="THIN FROTH", milkType="DAIRY"),
  espresso_steps("Single", "ESPRESSO", "a large mug") +
  froth_steps("milk up to the LATTE line", "THIN FROTH", extra="the chai powder") +
  ["Pour the spiced milk over the espresso."],
  flavor=["warm spice"])

R("affogato", "Affogato", "espresso", NINJA(), "hot", False, "quick", 2, "6.5 oz", "Small bowl or glass",
  ["Double shot of espresso", "1 to 2 scoops vanilla ice cream"],
  S("Double", "ESPRESSO"),
  ["Scoop the ice cream into a small bowl or glass and keep it in the freezer while you brew."] +
  espresso_steps("Double", "ESPRESSO", "an espresso cup") +
  ["Pour the hot espresso over the ice cream and serve right away."],
  flavor=["dessert", "sweet"])

R("spanish-latte", "Spanish Latte", "espresso",
  ("web", "Little Sugar Snaps", "https://www.littlesugarsnaps.com/spanish-latte/"),
  "hot", True, "quick", 4, "1 latte", "Small heatproof glass",
  ["Double shot of espresso", "1½ tbsp sweetened condensed milk (adjust to taste)", "3 oz (90 ml) whole milk"],
  S("Double", "ESPRESSO", froth="STEAMED MILK", milkType="DAIRY"),
  ["Warm the glass with hot water from the hot water spout, then empty it."] +
  espresso_steps("Double", "ESPRESSO", "the glass", cup_prep="Spoon the condensed milk into the warm glass.") +
  ["Stir until the condensed milk melts into the espresso."] +
  froth_steps("3 oz cold whole milk", "STEAMED MILK") +
  ["Top the glass with the hot milk and drink right away."],
  tips=["Make it iced: stir the condensed milk into the espresso, pour over ice and top with cold milk in equal parts to the coffee.",
        "For a foam top, use THIN FROTH instead of STEAMED MILK."],
  note="The original uses three 30 ml shots and heats the milk in a pan to 181°F. We use the Pro's double shot and the STEAMED MILK preset.",
  rating="5.0 ★ (2 ratings)", flavor=["sweet", "creamy"])

R("cafe-bombon", "Café Bombón", "espresso",
  ("web", "Starbucks at Home", "https://www.starbucksathome.com/recipes/bombon-recipe-ndg"),
  "hot", True, "quick", 4, "1 drink", "Small clear glass",
  ["Double shot of espresso", "1 oz (30 ml) sweetened condensed milk", "2 oz (60 ml) milk"],
  S("Double", "ESPRESSO", froth="THICK FROTH", milkType="DAIRY"),
  ["Pour the condensed milk into the bottom of a small clear glass."] +
  espresso_steps("Double", "ESPRESSO", "a small pitcher or cup") +
  froth_steps("2 oz cold milk", "THICK FROTH") +
  ["Slowly pour the espresso over the back of a spoon onto the condensed milk so the layers stay separate.",
   "Spoon about 2 tbsp of the foam on top."],
  tips=["Stir before drinking, or sip the layers one at a time."],
  note="Brewed into a small pitcher first so it can be poured gently and keep the layers.",
  flavor=["sweet", "layered"])

R("pumpkin-spice-latte", "Pumpkin Spice Latte", "espresso",
  ("web", "Starbucks at Home", "https://athome.starbucks.com/recipe/pumpkin-spice-latte"),
  "hot", True, "fancy", 5, "1 latte", "Large mug",
  ["Double shot of espresso", "3 tbsp homemade pumpkin spice syrup (below)", "1 cup whole milk", "Whipped cream", "1 pinch pumpkin pie spice"],
  S("Double", "ESPRESSO", froth="THIN FROTH", milkType="DAIRY"),
  espresso_steps("Double", "ESPRESSO", "the mug", cup_prep="Add the pumpkin spice syrup to a large mug.") +
  ["Stir the syrup into the espresso."] +
  froth_steps("1 cup cold whole milk", "THIN FROTH") +
  ["Fill the mug about ¾ full with the frothed milk.", "Top with whipped cream and a pinch of pumpkin pie spice."],
  sub=[dict(name="Pumpkin spice syrup", ingredients=["1½ cups sugar", "1½ cups water", "6 cinnamon sticks", "1 tsp ground cloves", "1 tsp ground ginger", "2 tsp ground nutmeg", "4 tbsp pumpkin purée"],
            steps=["Bring the sugar and water to a simmer in a saucepan.", "Once the sugar dissolves, add the cinnamon sticks, cloves, ginger, nutmeg and pumpkin purée and simmer for 20 minutes.", "Take it off the heat and strain right away through cheesecloth. Keep it in the fridge."])],
  note="The original froths the milk in a Nespresso Aeroccino. THIN FROTH gives the same latte texture.",
  flavor=["warm spice", "seasonal"])

R("einspanner", "Einspänner (Viennese Coffee)", "espresso",
  ("web", "Tara's Multicultural Table", "https://tarasmulticulturaltable.com/einspanner-viennese-coffee/"),
  "hot", False, "fancy", 8, "1 drink", "8.5 oz footed glass mug",
  ["⅓ cup (80 ml) cold heavy cream", "About 1 tsp powdered or vanilla sugar (optional)", "Double shot of espresso (about 2 oz)", "2 tbsp hot water (optional)", "Chocolate shavings or cocoa powder (optional)"],
  S("Double", "ESPRESSO", hotWater="optional splash"),
  ["Whip the cold cream and sugar with a mixer until just a little stiffer than soft peaks. Stop before it gets stiff.",
   "Warm the glass with hot water from the hot water spout, then empty it."] +
  espresso_steps("Double", "ESPRESSO", "the warm glass") +
  ["Stir in 2 tbsp hot water if you'd like it a little longer.",
   "Pour the cream gently over the back of a spoon held just above the coffee to build a thick white layer.",
   "Finish with chocolate shavings or cocoa and serve right away."],
  tips=["Fiaker variation: stir 1 oz kirsch into the espresso before the cream.",
        "Cream that's too thin sinks; too stiff loses its silkiness."],
  rating="5.0 ★ (1 rating)", flavor=["rich", "creamy"])

# ======================================================================
# RISTRETTO
# ======================================================================
R("piccolo", "Piccolo Latte", "ristretto",
  ("web", "Nespresso", "https://nespresso.com/au/en/coffee-recipes/piccolo"),
  "hot", True, "quick", 3, "1 piccolo", "3 oz (90 ml) glass",
  ["Ristretto shot (about 40 ml)", "About 3½ oz (110 ml) milk"],
  S("Double", "RISTRETTO", froth="THIN FROTH", milkType="DAIRY"),
  espresso_steps("Double", "RISTRETTO", "a small 3 oz glass") +
  froth_steps("3½ oz cold milk", "THIN FROTH") +
  ["Gently swirl the shot, then pour the milk to the top of the glass, leaving about ½ inch of foam at the rim."],
  tips=["Tilt the glass and pour slowly if you want to try latte art."],
  flavor=["sweet", "velvety"])

R("melbourne-magic", "Melbourne Magic", "ristretto",
  ("web", "Lavazza", "https://lavazza.com.au/en/coffee-secrets/magic-coffee-recipe"),
  "hot", True, "quick", 3, "1 magic", "5.4 oz (160 ml) cup",
  ["Double ristretto (about 35 to 40 ml)", "Milk of your choice"],
  S("Double", "RISTRETTO", froth="THIN FROTH", milkType="DAIRY or PLANT-BASED"),
  espresso_steps("Double", "RISTRETTO", "a 160 ml (5.4 oz) cup") +
  froth_steps("cold milk, about 4 oz", "THIN FROTH", "DAIRY (or PLANT-BASED)") +
  ["Gently pour the silky milk into the ristretto and let them blend. Aim for a flat-white texture with very little foam."],
  tips=["Iced Magic: brew the ristretto, let it cool, pour over ice and add cold milk.",
        "Magic Mocha: stir 1 tsp cocoa or chocolate syrup into the ristretto before the milk.",
        "Flavored Magic: add vanilla, caramel or hazelnut syrup before the milk."],
  note="Lavazza doses 18 to 20 g; the Pro's Double basket doses about 18 g by weight automatically.",
  flavor=["bold", "velvety"])

R("ristretto-over-ice", "Ristretto Over Ice", "ristretto",
  ("web", "Nespresso", "https://www.nespresso.com/au/en/coffee-recipes/ristretto-over-ice"),
  "iced", False, "quick", 2, "1 drink", "Short glass",
  ["Ristretto shot (about 40 ml)", "3 ice cubes (90 g)", "3 oz (90 ml) cold water", "A few thin slices of fresh ginger (optional)"],
  S("Double", "RISTRETTO"),
  espresso_steps("Double", "RISTRETTO", "the glass", cup_prep="Put 3 ice cubes in a short glass.") +
  ["Pour the cold water over the ice and coffee.", "Add a few slices of fresh ginger if you like."],
  flavor=["bright", "refreshing"])

R("thyme-dark-choco-macchiato", "Thyme & Dark Chocolate Macchiato", "ristretto",
  ("web", "Nespresso", "https://nespresso.com/recipes/ch/en/37119RIS-ristretto-classico-thyme-dark-choco-macchiato.html"),
  "hot", True, "fancy", 4, "1 drink", "Espresso cup",
  ["Ristretto shot (about 25 to 40 ml)", "3½ oz (100 ml) low-fat milk", "A few fresh thyme leaves", "Dark chocolate, for grating"],
  S("Double", "RISTRETTO", froth="THICK FROTH", milkType="DAIRY"),
  espresso_steps("Double", "RISTRETTO", "an espresso cup") +
  froth_steps("3½ oz cold low-fat milk", "THICK FROTH") +
  ["Spoon the hot foam over the ristretto.", "Scatter a few thyme leaves on the foam and grate dark chocolate over the top."],
  note="Nespresso's version uses a 25 ml capsule and the Aeroccino cappuccino setting. THICK FROTH is the Pro's cappuccino foam.",
  flavor=["herbal", "chocolate"])

# ======================================================================
# LUNGO
# ======================================================================
R("iced-lungo", "Iced Lungo", "lungo",
  ("web", "Nespresso", "https://nespresso.com/recipes/us/en/23136ICE-iced-lungo.html"),
  "iced", False, "quick", 3, "1 drink", "Tall glass",
  ["Lungo shot", "3 ice cubes (90 g)", "1 tsp sugar (optional)"],
  S("Double", "LUNGO"),
  espresso_steps("Double", "LUNGO", "the shaker", cup_prep="Put 3 ice cubes and the sugar (if using) in a cocktail shaker.") +
  ["Put the lid on and shake hard for about 10 seconds until frothy.", "Pour into a tall glass."],
  note="Nespresso mixes 40 ml espresso with 100 ml cold water. The Pro's Double LUNGO brews that same longer volume in one go, so it goes straight onto the ice.",
  flavor=["refreshing", "smooth"])

R("iced-lungo-macchiato", "Iced Lungo Macchiato", "lungo",
  ("web", "Nespresso", "https://www.nespresso.com/recipes/us/en/063ICE-iced-lungo-macchiato.html"),
  "iced", True, "quick", 5, "1 drink", "Tall glass",
  ["Lungo shot", "Brown sugar, to taste", "4 to 5 tbsp crushed ice", "3 to 4 tbsp milk foam", "Chocolate powder (optional)"],
  S("Double", "LUNGO", froth="THICK FROTH", milkType="DAIRY"),
  espresso_steps("Double", "LUNGO", "a cup") +
  ["Stir in the brown sugar."] +
  froth_steps("cold milk up to the minimum fill line", "THICK FROTH") +
  ["Pour the lungo into a tall glass and add 4 to 5 tbsp crushed ice.", "Spoon 3 to 4 tbsp of the milk foam on top.", "Dust with chocolate powder if you like."],
  flavor=["smooth", "creamy"])

R("blueberry-lungo", "Blueberry Lungo", "lungo",
  ("web", "Nespresso", "https://www.nespresso.com/recipes/int/en/31151BLU-blueberry-lungo.html"),
  "hot", False, "quick", 2, "1 drink", "Clear 4 oz cup",
  ["1 tbsp (15 g) blueberry jam", "Lungo shot (about 110 ml)"],
  S("Double", "LUNGO"),
  espresso_steps("Double", "LUNGO", "the cup", cup_prep="Spoon the blueberry jam into the bottom of a clear cup.") +
  ["Stir before drinking, or let the jam sweeten the last sips."],
  note="Created by Nespresso mixologist Sacha Wittorski. A dark, bold roast works best.",
  flavor=["fruity"])

R("cafe-viennois", "Café Viennois", "lungo",
  ("web", "Nespresso", "https://nespresso.com/recipes/ca/en/23085CAF-cafe-viennois.html"),
  "hot", True, "quick", 4, "1 drink", "Lungo cup",
  ["Lungo shot (about 110 ml)", "Cold skim milk, up to the minimum line on the jug", "Dark chocolate, for grating"],
  S("Double", "LUNGO", froth="EXTRA-THICK FROTH", milkType="DAIRY"),
  espresso_steps("Double", "LUNGO", "a lungo cup") +
  froth_steps("cold skim milk up to the minimum fill line", "EXTRA-THICK FROTH") +
  ["Spoon the foam generously over the coffee.", "Grate a little dark chocolate on top."],
  note="Nespresso calls for very cold 0% milk for a dense foam. The Pro's EXTRA-THICK FROTH preset is made for exactly this.",
  flavor=["airy", "chocolate"])

# ======================================================================
# AMERICANO
# ======================================================================
R("americano", "Americano", "americano", NINJA_UKG, "hot", False, "quick", 2, "1 americano", "Mug",
  ["Fresh whole coffee beans", "Hot water"],
  S("Double", "AMERICANO"),
  espresso_steps("Double", "AMERICANO", "a mug") +
  ["When it finishes, top up with HOT WATER to your taste."],
  tips=["Press the strength button for a stronger (2:1) or longer (4:1) cup."],
  flavor=["clean", "bold"])

R("americano-con-crema", "Americano con Crema", "americano",
  ("web", "Starbucks at Home", "https://athome.starbucks.com/recipe/americano-con-crema"),
  "hot", True, "fancy", 10, "1 drink", "Mug",
  ["Double shot of espresso", "Orange syrup, to taste (below)", "¼ cup hot water", "2 tbsp (⅛ cup) milk", "Sugar, to sprinkle (optional)"],
  S("Double", "ESPRESSO", froth="EXTRA-THICK FROTH", milkType="DAIRY", hotWater="¼ cup"),
  froth_steps("2 tbsp cold milk (the jug's minimum line if 2 tbsp is too little)", "EXTRA-THICK FROTH") +
  ["Let the foam rest for 1 to 2 minutes while you brew."] +
  espresso_steps("Double", "ESPRESSO", "a mug", cup_prep="Add orange syrup to the mug.") +
  ["Add ¼ cup hot water from the hot water spout and stir.", "Top with a few spoonfuls of the milk foam and sprinkle with sugar if you like."],
  sub=[dict(name="Orange syrup", ingredients=["2 cups water", "½ cup sugar", "Peel or zest of ½ orange"],
            steps=["Simmer the water, sugar and orange peel over medium-high heat, stirring now and then, for about 5 minutes until the sugar dissolves.", "Let it cool, then strain into a jar."])],
  note="Starbucks blends the milk for 2 minutes to make a stiff foam. The EXTRA-THICK FROTH preset replaces the blender.",
  flavor=["citrus", "creamy"])

R("iced-americano", "Iced Americano", "americano",
  ("web", "A Couple Cooks", "https://www.acouplecooks.com/iced-americano/"),
  "iced", False, "quick", 2, "1 drink", "Glass",
  ["Double shot of espresso (about 2 oz)", "½ cup ice", "2 tbsp cold water (optional)"],
  S("Double", "ESPRESSO"),
  espresso_steps("Double", "ESPRESSO", "the glass", cup_prep="Fill a glass with ½ cup ice.") +
  ["Taste, then add up to 2 tbsp cold water if you want it milder."],
  tips=["Add a splash of oat milk, simple syrup, vanilla syrup or demerara syrup if you like."],
  rating="5.0 ★ (1 rating)", flavor=["clean", "refreshing"])

R("sparkling-long-black", "Sparkling Long Black Over Ice", "americano",
  ("web", "Nespresso", "https://www.nespresso.com/recipes/us/en/28479LON-long-black-over-ice.html"),
  "iced", False, "quick", 3, "1 drink", "Tall glass",
  ["4 ice cubes", "4 oz sparkling water", "Single shot of espresso (about 1 oz)", "2 tsp (10 ml) coconut syrup (optional)"],
  S("Single", "ESPRESSO"),
  ["Put 4 ice cubes in a tall glass and pour in the sparkling water. Give it a stir."] +
  espresso_steps("Single", "ESPRESSO", "the glass") +
  ["Add the coconut syrup if you like."],
  note="Nespresso uses a 25 ml extraction. The Pro's Single basket shot is the closest match.",
  flavor=["sparkling", "refreshing"])

# ======================================================================
# COLD PRESSED
# ======================================================================
R("iced-hazelnut-latte", "Iced Hazelnut Latte", "cold-pressed", NINJA(), "iced", True, "quick", 3, "9.5 oz", "12 oz glass",
  ["Double shot of cold-pressed espresso", "1 tbsp hazelnut syrup", "1 cup (8 oz) whole milk", "Ice"],
  S("Double", "COLD-PRESSED"),
  espresso_steps("Double", "COLD-PRESSED", "the glass", cup_prep="Fill a 12 oz glass with ice and add the hazelnut syrup.") +
  ["Pour in the milk and stir."],
  flavor=["nutty", "sweet"])

R("brown-sugar-oat-shaken", "Brown Sugar Oat Milk Shaken Latte", "cold-pressed", NINJA(), "iced", True, "quick", 3, "5.5 oz", "10 oz glass",
  ["Double shot of cold-pressed espresso", "1 tbsp brown sugar", "Ice", "½ cup (4 oz) oat milk"],
  S("Double", "COLD-PRESSED"),
  espresso_steps("Double", "COLD-PRESSED", "the shaker", cup_prep="Put the brown sugar and a handful of ice in a cocktail shaker.") +
  ["Shake hard for 15 seconds.", "Pour into a 10 oz glass and top with the oat milk."],
  flavor=["caramel", "creamy"])

R("iced-dirty-chai", "Iced Dirty Chai", "cold-pressed", NINJA(), "iced", True, "quick", 3, "11.5 oz", "16 oz glass",
  ["Double shot of cold-pressed espresso", "Ice", "¾ cup (6 oz) whole milk", "½ cup chai tea concentrate"],
  S("Double", "COLD-PRESSED"),
  espresso_steps("Double", "COLD-PRESSED", "the glass", cup_prep="Fill a 16 oz glass with ice.") +
  ["Add the milk and chai concentrate and stir."],
  flavor=["warm spice"])

R("espresso-martini", "Espresso Martini", "cold-pressed", NINJA(), "iced", False, "fancy", 3, "5.25 oz", "Martini glass",
  ["Double shot of cold-pressed espresso", "Ice", "¾ oz simple syrup", "1½ oz vodka", "1½ oz coffee liqueur", "3 espresso beans, to garnish (optional)"],
  S("Double", "COLD-PRESSED"),
  espresso_steps("Double", "COLD-PRESSED", "the shaker", cup_prep="Fill a cocktail shaker with ice.") +
  ["Add the simple syrup, vodka and coffee liqueur.", "Shake hard for 10 seconds and strain into a martini glass.", "Float 3 espresso beans on top."],
  tips=["Boozy cold foam version (Ninja): froth 2 oz heavy cream with ½ oz Irish cream and 1 tsp vanilla syrup on COLD FOAM, swap the simple syrup for 2 oz Irish cream, use 1 oz vodka, then spoon the foam over the strained martini."],
  alcohol=True, flavor=["boozy", "bold"])

R("iced-choc-strawberry-latte", "Iced Chocolate Strawberry Latte", "cold-pressed",
  NINJA_WEB("https://www.sharkninja.com/iced-chocolate-strawberry-latte/REC20033.html"),
  "iced", True, "fancy", 5, "1 drink", "16 oz glass",
  ["Ice", "3 tbsp strawberry syrup, divided", "1 tbsp chocolate syrup", "Double shot of cold-pressed espresso", "¼ cup (2 oz) heavy cream", "¾ cup (6 oz) whole milk"],
  S("Double", "COLD-PRESSED", froth="COLD FOAM", milkType="DAIRY"),
  espresso_steps("Double", "COLD-PRESSED", "the glass", cup_prep="Fill a 16 oz glass with ice and drizzle 1 tbsp strawberry syrup and the chocolate syrup over the ice.") +
  froth_steps("the heavy cream (to the 2 oz line)", "COLD FOAM", extra="the other 2 tbsp strawberry syrup") +
  ["Stir the milk into the espresso, then top with the strawberry cold foam."],
  sub=[dict(name="Strawberry syrup (make the night before)", ingredients=["½ cup chopped strawberries", "½ cup sugar"],
            steps=["Stir the strawberries and sugar together and refrigerate overnight.", "Strain. Keeps in the fridge for up to 1 week."])],
  flavor=["fruity", "chocolate"])

R("iced-caramel-macchiato", "Iced Caramel Macchiato", "cold-pressed",
  ("web", "Starbucks at Home", "https://athome.starbucks.com/recipe/iced-caramel-macchiato"),
  "iced", True, "quick", 5, "1 drink", "16 oz glass",
  ["1 oz vanilla syrup", "¾ cup cold 2% milk", "Ice", "Double shot of cold-pressed espresso", "Caramel sauce, to drizzle"],
  S("Double", "COLD-PRESSED"),
  ["Pour the vanilla syrup into a 16 oz glass, add the cold milk, then fill with ice to ½ inch below the rim."] +
  espresso_steps("Double", "COLD-PRESSED", "the glass") +
  ["Let the espresso layer on top, then finish with a crosshatch of caramel sauce."],
  sub=[dict(name="Vanilla syrup", ingredients=["1 cup sugar", "1 cup water", "1 vanilla bean, split (or 1½ tbsp vanilla extract)"],
            steps=["Bring the sugar, water and vanilla bean to a boil, then simmer 5 minutes.", "Cool, then remove the bean (or stir in the extract once cooled)."]),
       dict(name="Caramel sauce", ingredients=["½ cup brown sugar", "2 tbsp butter", "¼ cup half-and-half", "Pinch of salt"],
            steps=["Heat everything in a small saucepan over medium-low for 1 minute.", "Turn to low and simmer 10 minutes.", "Cool before using. Keeps 1 week in the fridge."])],
  note="Starbucks pours hot espresso shots. Cold-pressed keeps the ice from melting and gives cleaner layers.",
  flavor=["caramel", "vanilla", "layered"])

R("espresso-tonic", "Espresso Tonic", "cold-pressed",
  ("web", "A Couple Cooks", "https://www.acouplecooks.com/espresso-tonic"),
  "iced", False, "quick", 3, "1 drink", "8 oz glass",
  ["Ice", "4 oz (½ cup) tonic water", "Double shot of cold-pressed espresso (about 2 oz)", "Lemon or orange wedge"],
  S("Double", "COLD-PRESSED"),
  ["Fill an 8 oz glass with ice and pour in the tonic water."] +
  espresso_steps("Double", "COLD-PRESSED", "a small cup") +
  ["Pour the espresso gently over the tonic so it floats.", "Run the citrus wedge around the rim and drop it in."],
  tips=["Always tonic first, espresso second, or it foams over."],
  note="The original cools a hot double shot. Cold-pressed is already cool, so there's no wait.",
  rating="5.0 ★ (1 rating)", flavor=["sparkling", "citrus"])

R("shakerato", "Shakerato with Sweet Cream", "cold-pressed",
  ("web", "Starbucks at Home", "https://athome.starbucks.com/recipe/shakerato"),
  "iced", True, "fancy", 10, "1 drink", "Coupe or short glass",
  ["4 oz cold-pressed espresso (a quad shot)", "½ tbsp simple syrup", "Ice", "Sweet cream syrup, to taste (below)"],
  S("Luxe", "COLD-PRESSED"),
  espresso_steps("Luxe", "COLD-PRESSED", "the shaker", cup_prep="Fill a cocktail shaker with ice and add the simple syrup.") +
  ["Shake hard for 20 to 30 seconds until foamy.", "Strain into a glass and spoon the foam from the shaker on top.", "Add sweet cream syrup to taste."],
  sub=[dict(name="Sweet cream syrup", ingredients=["1 can (14 oz) sweetened condensed milk", "8 oz half-and-half (or whole milk)"],
            steps=["Warm the condensed milk and half-and-half over low heat, stirring often, for 5 to 10 minutes.", "Cool completely. Keeps 5 days in the fridge."])],
  note="Starbucks uses 4 oz chilled drip coffee. A Luxe-basket cold-pressed quad (about 4 oz) is the traditional Italian way and needs no chilling.",
  flavor=["foamy", "sweet"])

# ======================================================================
# CLASSIC COFFEE
# ======================================================================
R("cafe-au-lait", "Café au Lait", "classic", NINJA(), "hot", True, "quick", 5, "11 oz", "12 oz cup",
  ["6 oz brewed coffee", "5 oz whole milk"],
  S("Luxe", "CLASSIC", 6, froth="THICK FROTH", milkType="DAIRY"),
  coffee_steps("CLASSIC", 6, "a 12 oz cup") +
  froth_steps("5 oz cold whole milk", "THICK FROTH") +
  ["Pour the frothed milk into the coffee."],
  flavor=["mellow", "creamy"])

R("cafe-de-olla", "Café de Olla", "classic",
  ("web", "Saveur", "https://www.saveur.com/cafe-de-olla-recipe/"),
  "hot", False, "quick", 6, "1 mug", "12 oz mug",
  ["1 heaping tbsp piloncillo or dark brown sugar", "½ small cinnamon stick (Ceylon if you can), broken up", "10 oz brewed dark-roast coffee"],
  S("Luxe", "CLASSIC", 10),
  coffee_steps("CLASSIC", 10, "the mug",
               grounds_extra="Scatter the broken cinnamon stick over the grounds.",
               cup_prep="Put the piloncillo in a 12 oz mug.") +
  ["Stir until the piloncillo dissolves."],
  note="Saveur simmers 8 cups of water with the coffee, piloncillo and cinnamon in a clay pot. This is a one-mug version: the cinnamon brews with the grounds and the piloncillo melts in the cup. Use a dark roast.",
  flavor=["warm spice", "molasses"])

R("salted-caramel-apple-coffee", "Salted Caramel Apple Coffee", "classic",
  ("web", "Starbucks at Home", "https://athome.starbucks.com/recipe/salted-caramel-apple-crafted-coffee"),
  "hot", True, "fancy", 15, "1 mug", "12 oz mug",
  ["3 tbsp salted caramel apple syrup (below)", "6 oz brewed coffee", "4 oz whole milk", "Whipped cream, caramel drizzle, a dash of cinnamon, a rolled wafer cookie (any or all)"],
  S("Luxe", "CLASSIC", 6, froth="THIN FROTH", milkType="DAIRY"),
  coffee_steps("CLASSIC", 6, "the mug", cup_prep="Add the syrup to a 12 oz mug.") +
  ["Stir the syrup into the coffee."] +
  froth_steps("4 oz cold whole milk", "THIN FROTH") +
  ["Add the milk, then top with whipped cream, caramel, cinnamon or a rolled wafer cookie."],
  sub=[dict(name="Salted caramel apple syrup (keeps 7 days)", ingredients=["½ cup light brown sugar", "¾ cup water", "1 cup applesauce", "¾ cup caramel sauce", "¼ tsp cinnamon", "Dash of ground cloves", "¼ tsp salt"],
            steps=["Simmer the brown sugar and water over low heat until the sugar dissolves.", "Add the cinnamon, cloves, salt and applesauce and simmer 5 minutes.", "Strain through a fine-mesh strainer, stirring gently.", "Stir in the caramel sauce while warm. Refrigerate."])],
  flavor=["caramel", "apple", "seasonal"])

R("cardamom-coffee", "South Indian Cardamom Coffee", "classic",
  ("web", "Sunset", "https://sunset.com/recipe/cardamom-coffee"),
  "hot", True, "quick", 6, "1 large mug", "14 oz mug",
  ["Seeds from 1 cardamom pod, crushed", "¾ cup low-fat milk", "6 oz brewed coffee", "Sugar, to taste"],
  S("Luxe", "CLASSIC", 6, froth="STEAMED MILK", milkType="DAIRY"),
  froth_steps("¾ cup cold low-fat milk", "STEAMED MILK", extra="the crushed cardamom seeds") +
  ["Let the milk sit with the cardamom for a couple of minutes while you brew."] +
  coffee_steps("CLASSIC", 6, "a large mug") +
  ["Pour the milk through a small strainer into the coffee to catch the seeds.", "Sweeten to taste."],
  note="Sunset simmers the milk and cardamom for 5 minutes and drips 3 tbsp of fine-ground coffee with ⅔ cup water. The STEAMED MILK preset plus a short steep, and a 6 oz CLASSIC brew, match it.",
  flavor=["floral", "warm spice"])

# ======================================================================
# RICH COFFEE
# ======================================================================
R("irish-coffee-cold-foam", "Irish Coffee with Cold Foam", "rich", NINJA(), "hot", True, "fancy", 6, "14.25 oz", "16 oz glass mug",
  ["1 tbsp brown sugar", "10 oz brewed coffee", "1½ oz Irish whiskey", "1 tbsp whole milk", "2 oz heavy cream"],
  S("Luxe", "RICH", 10, froth="COLD FOAM", milkType="DAIRY"),
  coffee_steps("RICH", 10, "the mug", cup_prep="Put the brown sugar in a 16 oz glass mug.") +
  ["Stir in the whiskey."] +
  froth_steps("the milk and heavy cream", "COLD FOAM") +
  ["Spoon the cold foam over the hot coffee."],
  alcohol=True, flavor=["boozy", "creamy"])

R("mexican-spiced-coffee", "Mexican-Spiced Coffee with Chocolate Cold Foam", "rich",
  NINJA_WEB("https://www.sharkninja.com/mexican-spiced-coffee-with-chocolate-cold-foam/REC15864.html"),
  "hot", True, "fancy", 10, "12 oz", "14 oz mug",
  ["½ tsp cinnamon", "¼ tsp chili powder", "1 pinch cayenne", "10 oz brewed coffee", "2 oz heavy cream", "1 tsp powdered sugar", "2 tsp cocoa powder"],
  S("Luxe", "RICH", 10, froth="COLD FOAM", milkType="DAIRY"),
  coffee_steps("RICH", 10, "a 14 oz mug", grounds_extra="Sprinkle the cinnamon, chili powder and cayenne over the grounds and tap to spread them evenly.") +
  froth_steps("the heavy cream", "COLD FOAM", extra="the powdered sugar and cocoa") +
  ["Spoon the chocolate cold foam onto the coffee."],
  tips=["Make it iced: choose COLD-PRESSED and brew over ice."],
  flavor=["spicy", "chocolate"])

R("yuenyeung", "Hong Kong Yuenyeung (Coffee Milk Tea)", "rich",
  ("web", "Saveur", "https://www.saveur.com/drink/hong-kong-coffee-tea/"),
  "hot", True, "fancy", 15, "2 mugs", "Two 10 oz mugs",
  ["1½ tbsp loose black tea (or 3 tea bags, strings removed)", "1¼ cups water", "6 tbsp evaporated milk", "1 tbsp sweetened condensed milk", "8 oz brewed coffee"],
  S("Luxe", "RICH", 8),
  ["Bring the water and tea to a rolling boil in a small pot, then simmer hard for about 5 minutes until dark.",
   "Take it off the heat and stir in the evaporated and condensed milk.",
   "Heat again over medium-high until steaming, about 3 minutes, then strain into a teapot."] +
  coffee_steps("RICH", 8, "a carafe") +
  ["Stir the coffee into the milk tea and pour into two mugs. Or pour over ice for a cold version."],
  note="Saveur's recipe serves 4 with 2 cups of hot black coffee. This is halved, and RICH gives the strong coffee the drink needs.",
  flavor=["tea", "creamy"])

R("cafe-brulot", "Café Brûlot", "rich",
  ("web", "James Beard Foundation (Galatoire's, New Orleans)", "https://jamesbeard.org/recipes/cafe-brulot"),
  "hot", False, "fancy", 15, "6 demitasse cups", "Demitasse cups",
  ["2 oranges", "1 lemon", "12 cloves", "3 cinnamon sticks", "2 oz brandy", "2 oz orange liqueur (such as Cointreau)", "Two 18 oz batches of brewed French roast coffee, kept hot"],
  S("Luxe", "RICH", 18),
  coffee_steps("RICH", 18, "a carafe") +
  ["Brew a second 18 oz batch and keep both hot.",
   "Peel one orange in a single long spiral, stud it with the cloves and spear one end on a fork.",
   "Cut the lemon peel and the second orange's peel into ¼-inch twists.",
   "Warm the peels, cinnamon sticks, brandy and orange liqueur in a small pot over low heat for 3 to 5 minutes.",
   "Pour into a heatproof metal bowl. Take a ladleful and carefully light it.",
   "Hold the clove-studded spiral over the bowl and slowly pour the flaming liquor down it so the flame spirals into the bowl.",
   "Slowly pour in the hot coffee while stirring to put out the flame. Ladle into demitasse cups."],
  tips=["Do the flaming part away from anything that can catch, with a lid nearby."],
  note="The original calls for 6 cups of French roast. Two 18 oz RICH brews make about the same amount.",
  alcohol=True, flavor=["citrus", "boozy", "warm spice"])

R("honey-coffee", "Honey Coffee", "rich",
  ("web", "Taste of Home Test Kitchen", "https://www.tasteofhome.com/recipes/honey-coffee"),
  "hot", True, "quick", 8, "2 mugs", "Two mugs",
  ["8 oz strong brewed dark-roast coffee", "¼ cup whole milk", "2 tbsp honey", "1 small pinch ground cinnamon", "Tiny pinch nutmeg", "⅛ tsp vanilla extract"],
  S("Luxe", "RICH", 8, froth="STEAMED MILK", milkType="DAIRY"),
  coffee_steps("RICH", 8, "a carafe") +
  froth_steps("¼ cup cold whole milk (fill to the minimum line if needed)", "STEAMED MILK", extra="the honey, cinnamon and nutmeg") +
  ["Stir the hot spiced milk and the vanilla into the coffee and pour into mugs."],
  note="Taste of Home warms everything together in a pan and serves 4. This is halved, and the STEAMED MILK preset warms the milk, honey and spice in one go.",
  flavor=["honey", "warm spice"])

# ======================================================================
# OVER ICE
# ======================================================================
R("iced-salted-caramel-cold-foam", "Iced Coffee with Salted Caramel Cold Foam", "over-ice",
  NINJA_WEB("https://www.sharkninja.com/iced-coffee-with-salted-caramel-cold-foam/REC15849.html"),
  "iced", True, "quick", 10, "13 oz", "16 oz glass",
  ["10 oz over-ice coffee", "Ice", "2 oz heavy cream", "1 tbsp whole milk", "2 tsp caramel syrup", "¼ tsp kosher salt"],
  S("Luxe", "OVER ICE", 10, froth="COLD FOAM", milkType="DAIRY"),
  coffee_steps("OVER ICE", 10, "the glass", cup_prep="Fill a 16 oz glass with ice (take out the center drip tray if it doesn't fit).") +
  froth_steps("the cream and milk", "COLD FOAM", extra="the caramel syrup and salt") +
  ["Spoon the foam over the coffee."],
  tips=["Make it hot: choose CLASSIC, froth with THIN FROTH and skip the ice."],
  flavor=["caramel", "salty-sweet"])

R("iced-peppermint-cold-foam", "Iced Coffee with Peppermint Cold Foam", "over-ice", NINJA(), "iced", True, "quick", 6, "13 oz", "16 oz glass",
  ["10 oz over-ice coffee", "Ice", "2 oz heavy cream", "1 tbsp whole milk", "1 tbsp peppermint syrup"],
  S("Luxe", "OVER ICE", 10, froth="COLD FOAM", milkType="DAIRY"),
  coffee_steps("OVER ICE", 10, "the glass", cup_prep="Fill a 16 oz glass with ice.") +
  froth_steps("the cream and milk", "COLD FOAM", extra="the peppermint syrup") +
  ["Spoon the foam over the coffee."],
  tips=["Make it hot: choose CLASSIC and skip the ice."],
  flavor=["minty", "seasonal"])

R("vietnamese-iced-coffee", "Vietnamese-Style Iced Coffee", "over-ice", NINJA(), "iced", True, "quick", 5, "12 oz", "16 oz glass",
  ["10 oz over-ice coffee", "Ice", "3 tbsp sweetened condensed milk"],
  S("Luxe", "OVER ICE", 10),
  coffee_steps("OVER ICE", 10, "the shaker", cup_prep="Fill a cocktail shaker with ice and add the condensed milk.") +
  ["Shake for 10 seconds and pour into a 16 oz glass."],
  flavor=["sweet", "bold"])

R("thai-iced-coffee", "Thai Iced Coffee", "over-ice",
  ("web", "Hot Thai Kitchen (Pailin Chongchitnant)", "https://hot-thai-kitchen.com/thai-iced-coffee"),
  "iced", True, "quick", 8, "1 drink", "16 oz glass",
  ["6 oz over-ice coffee, from Thai coffee powder or a dark roast", "2 tbsp sweetened condensed milk", "2 tsp sugar, or to taste", "Pinch of salt", "Lots of ice", "2 to 3 tbsp evaporated milk"],
  S("Luxe", "OVER ICE", 6),
  coffee_steps("OVER ICE", 6, "the mixing glass", cup_prep="Stir the condensed milk, sugar and salt together in a mixing glass.") +
  ["Stir until dissolved. It should taste a little too strong and too sweet, because the ice will soften it.",
   "Fill a 16 oz glass all the way with ice and pour the coffee over it.",
   "Drizzle the evaporated milk on top so it cascades down, then stir before drinking."],
  tips=["Thai coffee powders (like Oliang) often include roasted grains. If yours does, it won't work in the grinder: brew it in a French press with ¾ cup hot water for 5 minutes instead."],
  note="Pailin steeps 3 tbsp Thai coffee powder in ¾ cup off-the-boil water. The Pro's OVER ICE program brews a strong 6 oz from whole dark-roast beans instead.",
  flavor=["sweet", "creamy"])

R("japanese-iced-coffee", "Japanese Iced Coffee", "over-ice",
  ("web", "Just One Cookbook (Nami)", "https://www.justonecookbook.com/japanese-iced-coffee/"),
  "iced", False, "quick", 5, "2 glasses", "Two 12 oz glasses",
  ["Light or medium roast beans", "Ice"],
  S("Luxe", "OVER ICE", 12),
  coffee_steps("OVER ICE", 12, "a carafe or large glass jug", cup_prep="Fill a carafe about a third full with ice.") +
  ["Swirl until chilled, then pour over fresh ice in two glasses."],
  note="Nami pour-overs 30 g of beans with 370 ml of 205°F water by hand. OVER ICE runs the same hot, flash-chilled method automatically.",
  flavor=["bright", "clean"])

R("iced-cinnamon-honey-coffee", "Iced Cinnamon Honey Coffee", "over-ice",
  ("web", "Starbucks at Home", "https://athome.starbucks.com/recipe/iced-cinnamon-honey-coffee"),
  "iced", True, "fancy", 25, "1 drink", "16 oz glass",
  ["8 oz over-ice coffee", "Ice", "Cinnamon honey syrup, to taste (below)", "Splash of milk of your choice"],
  S("Luxe", "OVER ICE", 8),
  coffee_steps("OVER ICE", 8, "the glass", cup_prep="Fill a 16 oz glass with ice.") +
  ["Add a splash of milk and some cinnamon honey syrup, stir, and adjust to taste."],
  sub=[dict(name="Cinnamon honey syrup", ingredients=["1 cup water", "2½ tbsp honey", "2 cinnamon sticks", "½ tsp vanilla extract"],
            steps=["Bring the water, honey and cinnamon sticks to a boil.", "Turn to low and simmer 10 minutes.", "Take it off the heat, stir in the vanilla and cool completely. Keep in the fridge."])],
  note="Starbucks brews double-strength coffee in a press. OVER ICE already brews double-strong for pouring over ice.",
  flavor=["honey", "warm spice"])

# ======================================================================
# COLD BREW
# ======================================================================
R("almond-caramel-cold-brew", "Almond Milk Caramel Cold Brew", "cold-brew", NINJA(), "iced", True, "quick", 6, "12 oz", "12 oz glass",
  ["10 oz cold brew", "Ice", "1 tbsp caramel syrup", "3 tbsp almond milk"],
  S("Luxe", "COLD BREW", 10),
  coffee_steps("COLD BREW", 10, "the glass", cup_prep="Fill a 12 oz glass with ice and add the caramel syrup.") +
  ["Add the almond milk and stir."],
  tips=["Make it hot: choose RICH and skip the ice."],
  flavor=["caramel", "nutty"])

R("cold-brew-cold-foam", "Cold Brew with Cold Foam", "cold-brew", NINJA_UKG, "iced", True, "quick", 10, "1 drink", "Medium glass",
  ["Fresh whole coffee beans", "Ice", "2 oz (60 ml) heavy cream", "1 oz (30 ml) whole milk"],
  S("Luxe", "COLD BREW", 12, froth="COLD FOAM", milkType="DAIRY"),
  coffee_steps("COLD BREW", 12, "the glass", cup_prep="Fill a medium glass with ice.") +
  froth_steps("the cream and milk", "COLD FOAM") +
  ["Spoon the cold foam over the cold brew."],
  tips=["For a thicker foam, use 3 oz heavy cream and no milk."],
  note="Ninja's UK guide uses size M (about 10 oz).",
  flavor=["smooth", "creamy"])

R("vanilla-sweet-cream-cold-brew", "Vanilla Sweet Cream Cold Brew", "cold-brew",
  ("web", "Oh, How Civilized (Jee Choe)", "https://www.ohhowcivilized.com/starbucks-vanilla-sweet-cream-cold-brew/"),
  "iced", True, "quick", 6, "16 oz", "16 oz glass",
  ["2 tbsp vanilla syrup (for the coffee)", "8 oz cold brew", "1 cup ice", "¼ cup half-and-half", "1 tbsp vanilla syrup (for the cream)"],
  S("Luxe", "COLD BREW", 8),
  ["Stir the half-and-half and 1 tbsp vanilla syrup together to make the sweet cream. Keep it cold."] +
  coffee_steps("COLD BREW", 8, "the glass", cup_prep="Add 2 tbsp vanilla syrup and 1 cup ice to a 16 oz glass.") +
  ["Pour the sweet cream over the top and watch it swirl down."],
  tips=["Starbucks-style sweet cream: 6 oz heavy cream, 3 oz 2% milk and 1 oz vanilla syrup. Keeps 4 days."],
  rating="4.75 ★ (35 ratings)", flavor=["vanilla", "creamy"])

R("salted-caramel-cream-cold-brew", "Salted Caramel Cream Cold Brew", "cold-brew",
  ("web", "The Big Man's World (Arman Liew)", "https://thebigmansworld.com/salted-caramel-cream-cold-brew/"),
  "iced", True, "quick", 6, "1 drink", "16 oz glass",
  ["8 oz cold brew", "Ice", "1 tbsp caramel syrup, divided", "2 tbsp heavy cream", "Pinch of salt (about ⅛ tsp)"],
  S("Luxe", "COLD BREW", 8, froth="COLD FOAM", milkType="DAIRY"),
  coffee_steps("COLD BREW", 8, "the glass", cup_prep="Fill a 16 oz glass with ice and add half the caramel syrup.") +
  ["Stir."] +
  froth_steps("the heavy cream (fill to the jug's minimum line, doubling the cream if needed)", "COLD FOAM", extra="the rest of the caramel syrup") +
  ["Pour the foam over the cold brew and sprinkle with the salt."],
  note="Arman whips the foam with a handheld frother. The Pro's COLD FOAM preset does the same. Half-and-half won't hold a foam, so use heavy cream.",
  rating="5.0 ★ (35 ratings)", flavor=["caramel", "salty-sweet"])

R("pumpkin-cream-cold-brew", "Pumpkin Cream Cold Brew", "cold-brew",
  ("web", "Tasting Table", "https://www.tastingtable.com/1666470/diy-starbucks-pumpkin-cream-cold-brew-recipe/"),
  "iced", True, "quick", 8, "2 drinks", "Two 12 oz glasses",
  ["12 oz cold brew (two 6 oz pours)", "Ice", "½ cup half-and-half or heavy cream", "2 tbsp vanilla syrup", "1 tbsp pumpkin purée", "¼ tsp ground cinnamon", "1 pinch nutmeg"],
  S("Luxe", "COLD BREW", 12, froth="COLD FOAM", milkType="DAIRY"),
  coffee_steps("COLD BREW", 12, "a carafe of ice") +
  froth_steps("the cream", "COLD FOAM", extra="the vanilla syrup, pumpkin purée, cinnamon and nutmeg") +
  ["Fill two glasses with ice and pour 6 oz of cold brew into each.", "Top with the pumpkin cream."],
  note="Tasting Table steeps cold brew for 12 hours. The Pro's COLD BREW program makes it in minutes, and COLD FOAM replaces the immersion blender. Heavy cream foams best.",
  rating="5.0 ★ (41 ratings)", flavor=["seasonal", "warm spice"])

# ======================================================================
# HOT WATER
# ======================================================================
R("mocha-whipped-iced-coffee", "Mocha Whipped Iced Coffee", "hot-water",
  NINJA_WEB("https://www.sharkninja.com/mocha-whipped-iced-coffee/REC20038.html"),
  "iced", True, "quick", 5, "1 drink", "12 oz glass",
  ["2 tbsp hot water", "2 tbsp sugar", "2 tbsp instant coffee", "1 tsp cocoa powder", "¾ cup (6 oz) whole milk", "Ice"],
  S(froth="COLD FOAM", milkType="DAIRY", hotWater="6 oz"),
  hot_water_steps("an 8 oz mug", "6 oz", "HIGH") +
  ["Pour 2 tbsp of the hot water into the milk jug and add the sugar, instant coffee and cocoa. (You won't need the rest of the water.)",
   "Set the jug on the frothing platform, press MILK TYPE until DAIRY lights up, turn the froth dial to COLD FOAM and press START FROTH.",
   "Pour the milk into a 12 oz glass of ice and spoon the whipped mocha on top."],
  flavor=["chocolate", "whipped"])

R("matcha-latte", "Matcha Latte", "hot-water",
  ("web", "Love and Lemons", "https://www.loveandlemons.com/matcha-latte/"),
  "hot", True, "quick", 4, "1 latte", "Large mug",
  ["½ to 1 tsp matcha powder, sifted", "¼ cup hot water", "¼ cup coconut milk (light or full-fat)", "Maple syrup or honey, to taste (optional)"],
  S(froth="STEAMED MILK", milkType="PLANT-BASED", hotWater="LOW"),
  ["Sift the matcha into a large mug."] +
  hot_water_steps("a small measuring cup", "the smallest size", "LOW") +
  ["Pour ¼ cup of the hot water over the matcha and whisk briskly up and down for about 30 seconds until frothy."] +
  froth_steps("¼ cup coconut milk (fill to the minimum line if needed)", "STEAMED MILK", "PLANT-BASED") +
  ["Add the warm milk to the mug and whisk again until combined.", "Sweeten to taste."],
  tips=["Whisk up and down, not in circles, for the best foam.", "Very hot water makes matcha bitter, which is why we use the LOW setting."],
  rating="4.86 ★ (35 ratings)", flavor=["grassy", "creamy"])

R("london-fog", "London Fog Latte", "hot-water",
  ("web", "Baking Mischief", "https://bakingmischief.com/london-fog-latte/"),
  "hot", True, "quick", 8, "8 oz", "8 oz mug",
  ["2 Earl Grey tea bags", "½ cup hot water", "2 tsp sugar", "½ cup milk", "1 tbsp heavy cream (optional)", "⅛ tsp vanilla extract (optional)"],
  S(froth="THIN FROTH", milkType="DAIRY", hotWater="HIGH"),
  ["Put the tea bags in an 8 oz mug."] +
  hot_water_steps("the mug", "the smallest size, stopping at ½ cup", "HIGH") +
  ["Steep for 5 minutes, then remove the tea bags and stir in the sugar."] +
  froth_steps("½ cup cold milk", "THIN FROTH") +
  ["Pour most of the milk into the tea, stir in the cream and vanilla, then add the last of the milk and foam."],
  tips=["Start with 1 tsp sugar if you like it less sweet.", "Use decaf Earl Grey for evenings, or pour over ice for an iced fog."],
  flavor=["floral", "vanilla"])

R("hot-toddy", "Classic Hot Toddy", "hot-water",
  ("web", "Cookie and Kate", "https://cookieandkate.com/classic-hot-toddy-recipe/"),
  "hot", False, "quick", 3, "1 drink", "Mug",
  ["¾ cup hot water", "1½ oz whiskey", "2 to 3 tsp honey", "2 to 3 tsp lemon juice", "1 lemon round", "1 cinnamon stick (optional)"],
  S(hotWater="HIGH, 6 oz"),
  hot_water_steps("a mug", "6 oz", "HIGH") +
  ["Add the whiskey, 2 tsp honey and 2 tsp lemon juice and stir until the honey dissolves.",
   "Taste and add up to 1 more tsp of honey or lemon.",
   "Garnish with a lemon round and a cinnamon stick."],
  tips=["Swap the whiskey for brandy or dark rum.", "Steep a black or green tea bag in the water for 2 to 3 minutes first."],
  note="The original simmers water in a kettle; 6 oz on HIGH from the hot water spout is about ¾ cup.",
  alcohol=True, flavor=["honey", "citrus", "boozy"])


# ======================================================================
# ROUND 2 (2026-11-21): bring every category to 5 outside picks
# ======================================================================
R("cafe-cubano", "Café Cubano", "espresso",
  ("web", "Starbucks at Home", "https://athome.starbucks.com/recipe/cafe-cubano"),
  "hot", False, "fancy", 5, "2 small cups", "Two espresso cups",
  ["Double shot of dark-roast espresso", "4 heaping tsp granulated sugar"],
  S("Double", "ESPRESSO"),
  ["Put the sugar in a small metal pitcher or mug."] +
  espresso_steps("Double", "ESPRESSO", "a second small cup") +
  ["As soon as the first few drops come out, take 1 tsp of the espresso and pour it onto the sugar.",
   "With the back of the spoon, grind the sugar and coffee against the side of the pitcher for 60 seconds until it's a smooth, pale paste.",
   "When the shot finishes, pour it very slowly into the sugar paste and stir gently. A light-tan foam (the espumita) rises to the top.",
   "Pour into espresso cups so each gets a layer of foam."],
  note="Starbucks brews it in a stovetop moka pot. The Pro's double shot replaces the moka pot; the sugar-whipping is the same.",
  flavor=["sweet", "bold"])

R("almond-lemon-brulee", "Ristretto Almond Lemon Brûlée", "ristretto",
  ("web", "Nespresso", "https://nespresso.com/recipes/int/en/35206RIS-ristretto-almond-lemon-brulee.html"),
  "hot", True, "fancy", 6, "1 drink", "Small clear glass",
  ["Ristretto shot (about 25 to 40 ml)", "3½ oz (100 ml) low-fat milk", "About ¾ tsp (3 g) brown sugar", "A few toasted almonds, chopped", "A little grated lemon peel"],
  S("Double", "RISTRETTO", froth="THICK FROTH", milkType="DAIRY"),
  espresso_steps("Double", "RISTRETTO", "a small clear glass") +
  froth_steps("3½ oz cold low-fat milk", "THICK FROTH") +
  ["Spoon the hot foam onto the ristretto.",
   "Sprinkle the brown sugar over the foam and caramelize it with a kitchen torch, like a crème brûlée.",
   "Scatter the toasted almonds and lemon peel on top."],
  tips=["No torch? Skip the caramelizing and just sprinkle the sugar on; it's still lovely."],
  note="Nespresso uses a 25 ml capsule and the Aeroccino cappuccino setting. THICK FROTH is the Pro's cappuccino foam.",
  flavor=["nutty", "citrus", "dessert"])

R("stockholm-spice", "Stockholm Spice Lungo", "lungo",
  ("web", "Nespresso (mixologist Sacha Wittorski)", "https://www.nespresso.com/recipes/int/en/34492STO-stockholm-spice.html"),
  "hot", False, "quick", 3, "1 drink", "Clear lungo cup",
  ["Lungo shot (about 110 ml), dark roast", "About 1 tsp (5 g) ground cinnamon", "About 1 tsp (5 g) freshly grated nutmeg", "1 whole clove", "1 tsp (4 g) sugar (optional)"],
  S("Double", "LUNGO"),
  ["Put the cinnamon, nutmeg, clove and sugar (if using) in the cup. Or tie the spices in a paper tea filter for a cleaner cup."] +
  espresso_steps("Double", "LUNGO", "the cup") +
  ["Stir and let it sit for a moment before drinking."],
  flavor=["warm spice", "bold"])

R("spiced-americano", "Spiced Americano with Cinnamon Whipped Cream", "americano",
  ("web", "Food Network (Giada De Laurentiis)", "https://www.foodnetwork.com/recipes/giada-de-laurentiis/spiced-americano-with-cinnamon-whipped-cream-recipe-1937579"),
  "hot", False, "fancy", 17, "1 drink (syrup makes plenty)", "6 to 8 oz cup",
  ["Double shot of espresso (about 2 oz)", "2 oz hot water", "2 tbsp spiced syrup (below)", "¼ cup heavy cream", "1½ tsp powdered sugar", "Ground cinnamon, for dusting"],
  S("Double", "ESPRESSO", hotWater="2 oz"),
  ["Whip the cream to soft peaks, add the powdered sugar and whip until stiff."] +
  espresso_steps("Double", "ESPRESSO", "a 6 to 8 oz cup") +
  ["Add 2 oz hot water from the hot water spout and 2 tbsp spiced syrup, and stir.",
   "Top with a dollop of whipped cream and dust with cinnamon."],
  sub=[dict(name="Spiced syrup (enough for about 8 drinks)", ingredients=["½ cup water", "1 cup sugar", "¼ tsp ground allspice", "¼ tsp ground cinnamon", "¼ tsp ground ginger"],
            steps=["Bring the water and sugar to a boil over medium heat, then turn to low.", "Add the spices and simmer 5 minutes. Cool and keep in the fridge."])],
  note="Giada's version makes 4 cups from 1 cup of espresso and 1 cup of boiling water. This is one cup, using the Pro's double shot and hot water spout.",
  flavor=["warm spice", "creamy"])

R("red-eye", "Red Eye", "americano",
  ("web", "KitchenAid", "https://www.kitchenaid.ca/en_ca/blog/recipes/red-eye-coffee.html"),
  "hot", False, "quick", 5, "1 large mug", "Large 16 oz mug",
  ["Double shot of espresso", "10 oz brewed coffee"],
  S("Double", "ESPRESSO"),
  espresso_steps("Double", "ESPRESSO", "a large 16 oz mug") +
  ["Tap the used grounds out of the portafilter."] +
  coffee_steps("CLASSIC", 10, "the same mug") +
  ["Drink it black, or add milk to taste."],
  tips=["For a 'black eye', use a quad shot (Luxe basket) instead of a double."],
  note="KitchenAid's machine brews a double shot and then drip coffee into the same mug. The Pro does both: espresso first, then a CLASSIC brew on top.",
  flavor=["bold", "extra strong"])

R("iced-coconut-coffee", "Iced Coconut Coffee", "cold-pressed",
  ("web", "Starbucks at Home", "https://www.starbucksathome.com/au/recipes/iced-coconut-coffee"),
  "iced", True, "quick", 3, "1 drink", "12 oz glass",
  ["Single shot of cold-pressed espresso", "2 oz (60 ml) cold water", "1 tsp coconut sugar", "6 to 8 ice cubes, crushed", "1 cup (250 ml) coconut milk drink"],
  S("Single", "COLD-PRESSED"),
  ["Put the coconut sugar and crushed ice in a glass, pour in the coconut milk and stir well."] +
  espresso_steps("Single", "COLD-PRESSED", "a small cup") +
  ["Stir the cold water into the espresso, then pour it over the coconut milk and watch it swirl."],
  note="Starbucks brews a capsule shot with 60 ml extra water and chills it. A cold-pressed single shot plus 60 ml cold water gives the same chilled americano with no wait.",
  flavor=["tropical", "creamy"])

R("iced-honey-oat-coffee", "Iced Honey Oat Coffee", "cold-pressed",
  ("web", "Starbucks at Home", "https://www.starbucksathome.com/gb/recipes/iced-honey-oat-coffee-recipe"),
  "iced", True, "quick", 3, "1 drink", "10 oz glass",
  ["6 to 8 ice cubes", "Single shot of cold-pressed espresso", "2 oz (60 ml) cold water", "1 tbsp honey", "⅓ cup (80 ml) unsweetened oat milk"],
  S("Single", "COLD-PRESSED"),
  espresso_steps("Single", "COLD-PRESSED", "the glass", cup_prep="Fill a glass with the ice.") +
  ["Add the cold water.",
   "Drizzle in the honey slowly and stir well so it dissolves.",
   "Top with the oat milk."],
  note="Starbucks brews a capsule americano over ice. A cold-pressed single shot plus 60 ml cold water matches it, and the honey still dissolves if you stir well.",
  flavor=["honey", "creamy"])

R("cinnamon-mocha-coffee", "Cinnamon Mocha Coffee", "classic",
  ("web", "Taste of Home Test Kitchen", "https://www.tasteofhome.com/recipes/cinnamon-mocha-coffee/"),
  "hot", True, "quick", 6, "1 mug", "12 oz mug",
  ["⅛ tsp + a pinch ground cinnamon", "8 oz brewed coffee", "¼ cup 2% milk", "1½ to 2 tsp sugar", "1½ tsp baking cocoa", "¼ tsp vanilla extract", "Cinnamon stick and whipped cream (optional)"],
  S("Luxe", "CLASSIC", 8, froth="STEAMED MILK", milkType="DAIRY"),
  coffee_steps("CLASSIC", 8, "a carafe", grounds_extra="Sprinkle the cinnamon evenly over the grounds.") +
  froth_steps("¼ cup cold 2% milk (fill to the jug's minimum line if needed)", "STEAMED MILK", extra="the sugar, cocoa and vanilla") +
  ["Pour the hot chocolate milk into a mug, then add the cinnamon coffee.",
   "Add a cinnamon stick and whipped cream if you like."],
  note="Taste of Home brews 4 cups with the cinnamon in the basket and heats the chocolate milk in a pan. This is one mug, with STEAMED MILK doing the pan's job.",
  flavor=["chocolate", "warm spice"])

R("bulletproof-coffee", "Bulletproof Coffee", "classic",
  ("web", "The Big Man's World (Arman Liew)", "https://thebigmansworld.com/keto-bulletproof-coffee/"),
  "hot", False, "quick", 3, "1 mug", "10 oz mug",
  ["8 oz brewed coffee", "1 tbsp + 1 tsp grass-fed butter (or ghee)", "1 tbsp MCT oil"],
  S("Luxe", "CLASSIC", 8),
  coffee_steps("CLASSIC", 8, "a blender-safe jug") +
  ["Add the butter and MCT oil and blend for 30 seconds until frothy.", "Pour into a mug."],
  tips=["No blender: melt the butter in the mug, add the rest and froth with a handheld frother.",
        "Add 1 tsp vanilla extract or a pinch of cinnamon for flavor."],
  rating="5.0 ★ (16 ratings)", flavor=["rich", "buttery"])

R("vietnamese-egg-coffee", "Vietnamese Egg Coffee (Cà Phê Trứng)", "rich",
  ("web", "Tara's Multicultural Table", "https://tarasmulticulturaltable.com/ca-phe-trung-vietnamese-egg-coffee/"),
  "hot", False, "fancy", 12, "1 drink", "Small heatproof glass",
  ["2 large pasteurized egg yolks", "¼ cup (60 ml) sweetened condensed milk", "½ tsp vanilla extract", "½ cup (4 oz) brewed dark-roast coffee", "Ground cinnamon or cocoa, to top"],
  S("Luxe", "RICH", 6),
  ["Beat the egg yolks, condensed milk and vanilla with a hand mixer for about 5 minutes, until thick and very pale. A drizzle should hold its shape on top for a moment."] +
  coffee_steps("RICH", 6, "a cup") +
  ["Pour ½ cup of the hot coffee into a small heatproof glass.",
   "Spoon the egg cream slowly over the back of a spoon onto the coffee so it forms a thick separate layer.",
   "Dust with cinnamon or cocoa and serve right away."],
  tips=["Use pasteurized eggs, since the yolks aren't cooked.", "A milk frother won't whip it thick enough; use a hand mixer.", "Hanoi cafés set the glass in a bowl of hot water to keep it warm."],
  note="Tara drips coarse Vietnamese coffee through a phin and says ½ cup strong brewed coffee works too. The Pro's RICH brew gives that strong coffee; use a dark roast.",
  flavor=["custardy", "sweet", "dessert"])

R("caramel-mocha", "Caramel Mocha", "rich",
  ("web", "Taste of Home Test Kitchen", "https://www.tasteofhome.com/recipes/creamy-caramel-mocha"),
  "hot", True, "fancy", 10, "1 large mug", "14 oz mug",
  ["2 tbsp heavy cream", "¾ tsp powdered sugar", "¼ tsp vanilla extract, divided", "1 tbsp Dutch-processed cocoa", "6 tbsp half-and-half", "8 oz strong brewed coffee", "2 tbsp caramel syrup", "Butterscotch-caramel topping, to drizzle"],
  S("Luxe", "RICH", 8, froth="STEAMED MILK", milkType="DAIRY"),
  ["Whip the heavy cream until it thickens, add the powdered sugar and a few drops of the vanilla, and whip to stiff peaks."] +
  froth_steps("the half-and-half (fill to the jug's minimum line if needed)", "STEAMED MILK", extra="the cocoa") +
  coffee_steps("RICH", 8, "a 14 oz mug", cup_prep="Add the caramel syrup and the rest of the vanilla to the mug.") +
  ["Stir in the hot cocoa milk.", "Top with the whipped cream and a drizzle of butterscotch."],
  note="Taste of Home makes 6 servings on the stove and says to divide by four for a smaller batch. This is that small batch in one mug, with STEAMED MILK warming the cocoa and half-and-half.",
  flavor=["caramel", "chocolate"])

R("mazagran", "Mazagran (Coffee Lemonade)", "over-ice",
  ("web", "Seattle Coffee Gear", "https://www.seattlecoffeegear.com/blogs/scg-blog/coffee-collaboration-portuguese-mazagran-coffee-coffee-lemonade-treat"),
  "iced", False, "quick", 6, "1 drink", "12 oz+ glass",
  ["About 3½ oz (100 g) ice for the carafe", "2 oz (56 g) fresh lemon juice", "¼ cup (56 g) sugar", "2 oz (56 g) water", "10 oz over-ice coffee, light roast", "Fresh ice, for serving"],
  S("Luxe", "OVER ICE", 10),
  ["In a carafe with about 3½ oz of ice, stir the sugar, lemon juice and water together to make a strong lemonade."] +
  coffee_steps("OVER ICE", 10, "the carafe") +
  ["Stir, then pour into a 12 oz or bigger glass of fresh ice."],
  note="Seattle Coffee Gear brews 25 g of light roast in an AeroPress with 300 g of water straight onto the lemonade. The Pro's OVER ICE brew lands on the lemonade the same way.",
  flavor=["citrus", "refreshing"])

R("iced-hazelnut-coffee", "Iced Hazelnut Coffee", "over-ice",
  ("web", "Starbucks at Home", "https://athome.starbucks.com/recipe/iced-hazelnut-coffee"),
  "iced", True, "quick", 4, "1 drink", "Tall glass",
  ["1½ cups ice", "1½ tsp hazelnut syrup", "6 oz over-ice coffee", "2 oz milk of your choice"],
  S("Luxe", "OVER ICE", 6),
  coffee_steps("OVER ICE", 6, "the glass", cup_prep="Fill a tall glass with the ice and add the hazelnut syrup.") +
  ["Top with the milk and stir until the syrup is mixed in."],
  note="Starbucks pours 4 oz of brewed Pike Place over ice. The Pro's smallest OVER ICE size, 6 oz, is brewed strong for ice, so it lands about the same.",
  flavor=["nutty", "smooth"])

R("cold-brew-salted-honey-foam", "Cold Brew with Salted Honey Cold Foam", "cold-brew",
  ("web", "Starbucks at Home", "https://athome.starbucks.com/recipe/cold-brew-salted-honey-foam"),
  "iced", True, "quick", 6, "1 drink", "16 oz glass",
  ["8 oz cold brew", "Ice", "1½ tbsp honey syrup, divided (below)", "¼ cup skim milk (or a barista-style plant milk)", "Pinch of salt"],
  S("Luxe", "COLD BREW", 8, froth="COLD FOAM", milkType="DAIRY"),
  coffee_steps("COLD BREW", 8, "the glass", cup_prep="Fill a 16 oz glass with ice.") +
  ["Stir in about half the honey syrup."] +
  froth_steps("¼ cup cold skim milk (fill to the jug's minimum line if needed)", "COLD FOAM", extra="the rest of the honey syrup and the salt") +
  ["Pour or spoon the salted honey foam on top."],
  sub=[dict(name="Honey syrup", ingredients=["¼ cup honey", "¼ cup hot water"],
            steps=["Stir the honey into hot water from the hot water spout until dissolved. Keeps 2 weeks in the fridge."])],
  note="Starbucks mixes 4 oz cold brew concentrate with 4 oz water. The Pro's COLD BREW program brews it ready to drink, so use 8 oz straight. Their honey syrup recipe is on a separate page, so this is a simple 1:1 honey syrup.",
  flavor=["honey", "salty-sweet"])

R("cold-brew-coconut-milkshake", "Cold Brew Coconut Chocolate Milkshake", "cold-brew",
  ("web", "Starbucks at Home (with Tastemade)", "https://athome.starbucks.com/recipe/cold-brew-coconut-chocolate-milkshake"),
  "iced", True, "fancy", 6, "1 shake", "Milkshake glass",
  ["6 oz cold brew", "2 scoops coconut ice cream", "2 tbsp semisweet chocolate chips", "Whipped cream", "Toasted coconut"],
  S("Luxe", "COLD BREW", 6),
  coffee_steps("COLD BREW", 6, "a blender jar with a couple of ice cubes") +
  ["Add the coconut ice cream and chocolate chips and blend until smooth.", "Pour into a glass and top with whipped cream and toasted coconut."],
  note="Starbucks uses 4 oz of cold brew concentrate. The Pro's smallest cold brew is 6 oz of ready-to-drink cold brew; brewing onto a couple of ice cubes keeps it cold and thick.",
  flavor=["dessert", "tropical", "chocolate"])

R("medicine-ball", "Honey Citrus Mint Tea (Medicine Ball)", "hot-water",
  ("web", "Oh, How Civilized (Jee Choe)", "https://www.ohhowcivilized.com/starbucks-medicine-ball-tea/"),
  "hot", False, "quick", 7, "20 oz", "Large mug",
  ["1 green tea bag (a mint green tea is closest)", "1 peach herbal tea bag", "1¼ cups (10 oz) hot water", "1¼ cups lemonade, warmed", "1 tbsp honey"],
  S(hotWater="HIGH, 10 oz"),
  ["Put both tea bags in a large mug."] +
  hot_water_steps("the mug", "10 oz", "HIGH") +
  ["Steep for 5 minutes while you warm the lemonade in the microwave for about 1 minute.",
   "Remove the tea bags, stir in the honey and the warm lemonade."],
  tips=["Add a drop of peppermint extract for the Starbucks peppermint version.", "Swap the lemonade for the juice of a small lemon plus a little more honey."],
  note="Jee simmers the water, lemonade and tea together for 5 minutes. Here the hot water spout steeps the tea and the lemonade is warmed separately.",
  rating="4.6 ★ (20 ratings)", flavor=["citrus", "honey", "soothing"])

R("creamy-hot-cocoa", "Creamy Hot Cocoa", "hot-water",
  ("web", "Tastes Better From Scratch (Lauren Allen)", "https://tastesbetterfromscratch.com/creamy-hot-cocoa/"),
  "hot", True, "quick", 5, "1 mug", "12 oz mug",
  ["4 tsp unsweetened cocoa powder", "4 tsp sugar", "Small pinch of salt", "4 tsp hot water", "1 cup whole milk", "Scant ¼ tsp vanilla extract", "Whipped cream (optional)"],
  S(froth="STEAMED MILK", milkType="DAIRY", hotWater="HIGH, a splash"),
  ["Put the cocoa, sugar and salt in a mug.",
   "Add 4 tsp hot water from the hot water spout (HIGH) and stir into a smooth, glossy paste."] +
  froth_steps("1 cup cold whole milk", "STEAMED MILK") +
  ["Pour the hot milk into the mug while stirring, then stir in the vanilla.", "Top with whipped cream if you like."],
  note="Lauren makes 4 mugs on the stove and simmers the cocoa paste for 2 minutes. This is one mug, with the hot water spout for the paste and STEAMED MILK for the milk.",
  rating="5.0 ★ (127 ratings)", flavor=["chocolate", "cozy"])

# ======================================================================
# MORE RECIPES (added 2026-11-22): popular café drinks
# ======================================================================
ACC = lambda path: ("web", "A Couple Cooks (Sonja Overhiser)", "https://www.acouplecooks.com/" + path)
SBX = lambda path: ("web", "Starbucks at Home", "https://athome.starbucks.com/recipe/" + path)
VANILLA_SYRUP = dict(name="Vanilla syrup", ingredients=["½ cup sugar", "½ cup water", "2 tsp vanilla extract"],
    steps=["Warm the sugar and water in a small pan over medium heat for 1 to 2 minutes, stirring until the sugar dissolves. Don't let it simmer.",
           "Take it off the heat, stir in the vanilla and let it cool. Keeps in the fridge for about a month."])
LAVENDER_SYRUP = dict(name="Lavender syrup", ingredients=["½ cup sugar", "½ cup water", "¼ cup dried culinary lavender"],
    steps=["Bring the sugar, water and lavender to a simmer, stirring until the sugar dissolves.",
           "Turn off the heat, let it steep 20 minutes, then strain into a jar. Keeps in the fridge for about a month."])
BROWN_SUGAR_SYRUP = dict(name="Brown sugar syrup", ingredients=["½ cup packed dark brown sugar", "½ cup water"],
    steps=["Simmer the brown sugar and water, stirring, until dissolved and slightly thick.", "Cool before using. Keeps in the fridge for about 2 weeks."])

# ---------------- Espresso ----------------
R("vanilla-latte", "Vanilla Latte", "espresso", ACC("vanilla-latte/"),
  "hot", True, "quick", 4, "1 latte", "10 oz mug",
  ["Double shot of espresso (2 oz)", "4 oz (½ cup) whole milk or oat milk", "½ tbsp vanilla syrup"],
  S("Double", "ESPRESSO", froth="THIN FROTH", milkType="DAIRY or PLANT-BASED"),
  espresso_steps("Double", "ESPRESSO", "a 10 oz mug") +
  froth_steps("4 oz cold milk (fill to the minimum line if needed)", "THIN FROTH", "DAIRY (or PLANT-BASED)", extra="the vanilla syrup") +
  ["Pour the milk into the center of the espresso, finishing with a thin layer of foam."],
  tips=["Make it iced: brew on COLD-PRESSED over a glass of ice, stir in the syrup and pour in cold milk."],
  note="Sonja steams the syrup with the milk, so the Pro's jug does the same job.",
  sub=[VANILLA_SYRUP], rating="5.0 ★ (2 ratings)", flavor=["vanilla", "creamy"])

R("white-chocolate-mocha", "White Chocolate Mocha", "espresso", SBX("white-chocolate-mocha"),
  "hot", True, "quick", 4, "1 mug", "12 oz mug",
  ["4 tbsp white chocolate chips or chopped white chocolate", "Double shot of espresso", "1 cup (8 oz) 2% milk", "Whipped cream"],
  S("Double", "ESPRESSO", froth="THIN FROTH", milkType="DAIRY"),
  ["Put the white chocolate in a 12 oz mug and warm it in the microwave in 15-second bursts until soft."] +
  espresso_steps("Double", "ESPRESSO", "the mug") +
  ["Stir the hot espresso into the white chocolate until smooth."] +
  froth_steps("1 cup cold 2% milk (up to the LATTE line)", "THIN FROTH") +
  ["Pour the frothed milk into the mug and top with whipped cream."],
  note="Starbucks uses a single 1 oz shot. A double stands up better to the sweet white chocolate. Use the Single basket for theirs.",
  rating="5.0 ★ (8 ratings)", flavor=["sweet", "creamy"])

R("gingerbread-latte", "Gingerbread Latte", "espresso", ACC("gingerbread-latte/"),
  "hot", True, "fancy", 4, "1 latte", "10 oz mug",
  ["Double shot of espresso (2 oz)", "1 tbsp gingerbread syrup", "4 oz (½ cup) whole milk or oat milk", "Ground cinnamon, to garnish"],
  S("Double", "ESPRESSO", froth="THIN FROTH", milkType="DAIRY or PLANT-BASED"),
  espresso_steps("Double", "ESPRESSO", "a 10 oz mug", cup_prep="Put the gingerbread syrup in a 10 oz mug.") +
  ["Stir the syrup into the espresso."] +
  froth_steps("4 oz cold milk (fill to the minimum line if needed)", "THIN FROTH", "DAIRY (or PLANT-BASED)") +
  ["Pour the milk into the center of the espresso, finishing with foam, and dust with cinnamon."],
  sub=[dict(name="Gingerbread syrup", ingredients=["1 inch fresh ginger, peeled", "3 cinnamon sticks", "1 tbsp allspice berries (or 1½ tsp ground)", "½ cup brown sugar", "⅔ cup water", "1 tsp vanilla extract"],
            steps=["Toast the cinnamon and allspice in a small pan over medium-low heat for 2 minutes.",
                   "Add the ginger, water, brown sugar and vanilla. Keep at a low simmer for 15 to 20 minutes.",
                   "Strain and cool. Keeps in the fridge for about a month."])],
  rating="5.0 ★ (1 rating)", flavor=["warm spice", "sweet"])

R("lavender-latte", "Lavender Latte", "espresso", ACC("lavender-latte/"),
  "hot", True, "fancy", 4, "1 latte", "10 oz mug",
  ["Double shot of espresso (2 oz)", "1 tbsp lavender syrup", "4 oz (½ cup) whole milk or oat milk", "Dried lavender buds, to garnish (optional)"],
  S("Double", "ESPRESSO", froth="THIN FROTH", milkType="DAIRY or PLANT-BASED"),
  espresso_steps("Double", "ESPRESSO", "a 10 oz mug", cup_prep="Put the lavender syrup in a 10 oz mug.") +
  ["Stir the syrup into the espresso."] +
  froth_steps("4 oz cold milk (fill to the minimum line if needed)", "THIN FROTH", "DAIRY (or PLANT-BASED)") +
  ["Pour the milk into the center of the espresso, finishing with foam. Scatter a few lavender buds on top."],
  sub=[LAVENDER_SYRUP], rating="5.0 ★ (1 rating)", flavor=["floral", "sweet"])

R("caramelized-honey-latte", "Caramelized Honey Latte", "espresso", SBX("caramelized-honey-latte"),
  "hot", True, "fancy", 15, "1 latte (plus honey milk for 3 more)", "12 oz mug",
  ["½ cup honey, plus a drizzle to finish", "1 tsp water", "½ tsp lemon juice", "4 cups unsweetened milk", "Double shot of espresso (2 oz)"],
  S("Double", "ESPRESSO", froth="THIN FROTH", milkType="DAIRY"),
  ["Simmer the honey, water and lemon juice in a small pan over medium heat, stirring.",
   "Once it bubbles, stop stirring and let it cook 1 to 2 minutes until it darkens and smells nutty.",
   "Take the pan off the heat and slowly whisk in the 4 cups of milk. Let it cool a little. This is enough honey milk for 4 lattes; keep the rest in the fridge."] +
  espresso_steps("Double", "ESPRESSO", "a 12 oz mug") +
  froth_steps("1 cup of the honey milk (up to the LATTE line)", "THIN FROTH") +
  ["Pour the honey milk into the espresso and finish with a drizzle of honey."],
  note="Starbucks combines the warm honey milk with the espresso, then froths more milk on top. Frothing the honey milk itself does both in one step.",
  rating="5.0 ★ (1 rating)", flavor=["honey", "caramel"])

R("maple-pecan-latte", "Maple Pecan Latte", "espresso", ("web", "CopyKat (Stephanie Manley)", "https://copykat.com/starbucks-maple-pecan-latte/"),
  "hot", True, "quick", 4, "1 latte", "12 oz mug",
  ["Double shot of espresso", "2 tbsp maple syrup", "1 cup (8 oz) milk", "2 tbsp whipped cream", "1 tsp chopped pecans"],
  S("Double", "ESPRESSO", froth="THIN FROTH", milkType="DAIRY"),
  espresso_steps("Double", "ESPRESSO", "a 12 oz mug", cup_prep="Put the maple syrup in a 12 oz mug.") +
  froth_steps("1 cup cold milk (up to the LATTE line)", "THIN FROTH") +
  ["Stir the maple syrup into the espresso, add the milk and stir again.", "Top with whipped cream and the chopped pecans."],
  note="Stephanie uses a 1.5 oz shot. A Double basket shot is about 2 oz.",
  rating="5.0 ★ (6 ratings)", flavor=["maple", "nutty"])

R("cafe-con-leche", "Café con Leche", "espresso", ("web", "A Sassy Spoon (Ericka Sanchez)", "https://asassyspoon.com/cafe-con-leche/"),
  "hot", True, "quick", 4, "1 mug", "8 oz mug",
  ["Double shot of espresso (dark Cuban-style roast if you have it)", "½ cup (4 oz) whole milk", "2 tsp sugar, or to taste", "Pinch of salt (optional)"],
  S("Double", "ESPRESSO", froth="STEAMED MILK", milkType="DAIRY"),
  froth_steps("½ cup cold whole milk (fill to the minimum line if needed)", "STEAMED MILK") +
  ["Pour the hot milk into an 8 oz mug and stir in the sugar."] +
  espresso_steps("Double", "ESPRESSO", "a small cup") +
  ["Pour the espresso into the milk and stir until light brown. Taste, and add more sugar or a tiny pinch of salt if you like."],
  note="Ericka brews ¼ cup of moka-pot coffee. A Double basket shot is close to that, and STEAMED MILK replaces heating the milk in a pan.",
  rating="4.85 ★ (19 ratings)", flavor=["mellow", "sweet"])

# ---------------- Cold Pressed ----------------
R("iced-mocha", "Iced Mocha", "cold-pressed", ACC("iced-mocha/"),
  "iced", True, "quick", 4, "1 drink", "12 oz glass",
  ["Double shot of espresso (2 oz)", "1 tbsp chocolate chips", "1 tbsp simple syrup or chocolate syrup", "¼ cup (2 oz) milk or oat milk", "Ice"],
  S("Double", "ESPRESSO", froth="COLD FOAM", milkType="DAIRY or PLANT-BASED"),
  ["Put the chocolate chips in a heatproof jar."] +
  espresso_steps("Double", "ESPRESSO", "the jar") +
  ["Cover the jar and shake hard until the chocolate melts. Pour into a 12 oz glass full of ice."] +
  froth_steps("the milk and simple syrup (fill to the minimum line if needed)", "COLD FOAM", "DAIRY (or PLANT-BASED)") +
  ["Spoon the foamy milk over the chocolate espresso."],
  note="This one is brewed on ESPRESSO, not COLD-PRESSED: the hot shot is what melts the chocolate. Sonja shakes the milk in a jar to foam it; the COLD FOAM preset does it for you.",
  rating="5.0 ★ (1 rating)", flavor=["chocolate", "bold"])

R("iced-white-mocha", "Iced White Chocolate Mocha", "cold-pressed", ACC("iced-white-chocolate-mocha/"),
  "iced", True, "quick", 4, "1 drink", "12 oz glass",
  ["Double shot of espresso (2 oz)", "2 tbsp white chocolate chips", "2 tbsp milk", "Ice", "Cold foam: 2 oz heavy cream + 1 oz milk"],
  S("Double", "ESPRESSO", froth="COLD FOAM", milkType="DAIRY"),
  ["Put the white chocolate chips in a heatproof jar."] +
  espresso_steps("Double", "ESPRESSO", "the jar") +
  ["Cover and shake hard until the chocolate melts. Stir in the 2 tbsp milk and pour into a 12 oz glass full of ice."] +
  froth_steps("the heavy cream and milk", "COLD FOAM") +
  ["Spoon the cold foam over the top."],
  note="Brewed on ESPRESSO so the hot shot melts the white chocolate.",
  rating="5.0 ★ (1 rating)", flavor=["sweet", "creamy"])

R("iced-lavender-oat-latte", "Iced Lavender Oat Milk Latte", "cold-pressed",
  ("web", "We Are Not Martha (Sues)", "https://wearenotmartha.com/iced-lavender-oatmilk-latte-starbucks-copycat/"),
  "iced", True, "quick", 3, "1 drink", "16 oz glass",
  ["Double shot of cold-pressed espresso (2 oz)", "1 tbsp lavender syrup", "Ice", "10 oz barista-style oat milk"],
  S("Double", "COLD-PRESSED"),
  espresso_steps("Double", "COLD-PRESSED", "a 16 oz glass", cup_prep="Put the lavender syrup in a 16 oz glass.") +
  ["Stir, fill the glass with ice and top with the oat milk."],
  note="Sues makes a lavender sugar powder and uses blonde espresso; her notes say lavender syrup works too. Use a lighter roast if you have one.",
  sub=[LAVENDER_SYRUP], rating="5.0 ★ (2 ratings)", flavor=["floral", "creamy"])

R("iced-pistachio-latte", "Iced Pistachio Latte", "cold-pressed",
  ("web", "Seattle Coffee Gear", "https://www.seattlecoffeegear.com/blogs/scg-blog/iced-pistachio-latte-recipe"),
  "iced", True, "fancy", 3, "1 drink", "Tall glass",
  ["Double shot of cold-pressed espresso (2 oz)", "1 to 2 tbsp pistachio syrup", "Ice", "6 oz cold milk or plant milk", "Toasted pistachios, chopped, to garnish"],
  S("Double", "COLD-PRESSED"),
  espresso_steps("Double", "COLD-PRESSED", "the glass", cup_prep="Fill a tall glass with ice.") +
  ["Stir in the pistachio syrup, pour in the cold milk and top with chopped pistachios."],
  sub=[dict(name="Pistachio syrup", ingredients=["1 cup pistachios", "1 cup water", "1 cup sugar"],
            steps=["Lightly crush the pistachios in a small pan, add the water and sugar and bring to a boil.",
                   "Simmer 5 minutes, stirring now and then, then strain out the nuts and cool. Keeps 2 weeks in the fridge."])],
  flavor=["nutty", "sweet"])

R("dirty-matcha", "Iced Dirty Matcha Latte", "cold-pressed",
  ("web", "Tara's Multicultural Table", "https://tarasmulticulturaltable.com/iced-matcha-espresso-latte/"),
  "iced", True, "fancy", 5, "1 drink", "12 oz clear glass",
  ["1 tsp matcha powder, sifted", "2 tbsp hot water (not boiling)", "1 tbsp vanilla syrup or honey", "Ice", "½ cup (4 oz) cold milk", "Double shot of cold-pressed espresso (2 oz)"],
  S("Double", "COLD-PRESSED", hotWater="LOW"),
  ["Sift the matcha into a small bowl."] +
  hot_water_steps("a small cup", "the smallest size", "LOW") +
  ["Whisk 2 tbsp of the hot water into the matcha until smooth, then whisk in the vanilla syrup or honey.",
   "Pour the matcha into a clear 12 oz glass, fill with ice and slowly pour the milk over an ice cube so it layers on top."] +
  espresso_steps("Double", "COLD-PRESSED", "a small cup") +
  ["Slowly pour the espresso over an ice cube to make a third layer. Stir before drinking."],
  flavor=["grassy", "bold"])

R("toasted-vanilla-shaken", "Toasted Vanilla Oat Milk Shaken Espresso", "cold-pressed",
  ("web", "We Are Not Martha (Sues)", "https://wearenotmartha.com/iced-toasted-vanilla-oatmilk-shaken-espresso-starbucks-copycat/"),
  "iced", True, "fancy", 3, "1 grande", "16 oz glass",
  ["Triple shot of cold-pressed espresso (3 oz, light roast if you have it)", "1½ oz toasted vanilla syrup", "Ice", "4 oz (½ cup) oat milk"],
  S("Luxe", "COLD-PRESSED"),
  espresso_steps("Luxe", "COLD-PRESSED", "a cocktail shaker", cup_prep="Put the toasted vanilla syrup and a handful of ice in a cocktail shaker.") +
  ["Shake hard for about 20 seconds until frothy.", "Pour into a 16 oz glass of ice and top with the oat milk."],
  note="Sues uses 3 oz of espresso. The Luxe basket's cold-pressed shot is about that size.",
  sub=[dict(name="Toasted vanilla syrup", ingredients=["1 vanilla bean", "1 cup water", "1 cup sugar"],
            steps=["Split the vanilla bean, cut it into small pieces and toast them in a dry pan over medium-low heat for a few minutes, stirring, until fragrant.",
                   "Bring the water and sugar to a boil, lower the heat, add the vanilla and simmer about 10 minutes.",
                   "Cool, keeping the vanilla pieces in to infuse. Strain before using."])],
  rating="5.0 ★ (9 ratings)", flavor=["vanilla", "toasty"])

R("chocolate-almond-shaken", "Iced Chocolate Almond Milk Shaken Espresso", "cold-pressed", SBX("iced-chocolate-almond-shaken-espresso"),
  "iced", True, "quick", 3, "1 drink", "12 oz glass",
  ["Double shot of cold-pressed espresso", "1½ tbsp chocolate syrup, plus a drizzle", "1 cup ice, plus more for the glass", "½ cup (4 oz) almond milk"],
  S("Double", "COLD-PRESSED"),
  espresso_steps("Double", "COLD-PRESSED", "a cocktail shaker", cup_prep="Put the chocolate syrup and 1 cup ice in a cocktail shaker.") +
  ["Shake hard until frothy and ice cold.", "Strain into a glass full of ice, add the almond milk and drizzle with chocolate syrup."],
  rating="4.0 ★ (2 ratings)", flavor=["chocolate", "nutty"])

# ---------------- Over Ice ----------------
R("vanilla-iced-coffee", "Vanilla Iced Coffee", "over-ice", ACC("vanilla-iced-coffee/"),
  "iced", True, "quick", 4, "1 drink", "12 oz glass",
  ["Ice", "6 oz over-ice coffee", "¼ cup (2 oz) milk of your choice", "2 to 3 tsp vanilla syrup"],
  S("Luxe", "OVER ICE", 6),
  coffee_steps("OVER ICE", 6, "the glass", cup_prep="Fill a 12 oz glass with ice and add the vanilla syrup.") +
  ["Add the milk, stir and taste. Add more syrup or milk if you like."],
  note="Sonja uses ½ cup cold brew concentrate or strong coffee. OVER ICE brews it strong and hot straight onto the ice.",
  sub=[VANILLA_SYRUP], rating="5.0 ★ (2 ratings)", flavor=["vanilla", "smooth"])

R("brown-sugar-iced-coffee", "Brown Sugar Iced Coffee", "over-ice",
  ("web", "Coffee at Three", "https://coffeeatthree.com/iced-brown-sugar-coffee/"),
  "iced", True, "quick", 5, "1 drink", "12 oz glass",
  ["1 tbsp brown sugar", "2 tbsp hot water", "1 cup ice", "⅓ cup milk (any kind)", "6 oz over-ice coffee"],
  S("Luxe", "OVER ICE", 6, hotWater="HIGH, a splash"),
  ["Put the brown sugar in a 12 oz glass, add 2 tbsp hot water from the hot water spout and stir until dissolved.",
   "Add the ice and slowly pour in the milk."] +
  coffee_steps("OVER ICE", 6, "the glass") +
  ["Stir before drinking."],
  note="Coffee at Three uses ⅓ cup of cold brew or double-strength coffee. The 6 oz OVER ICE size gives a slightly bigger, equally strong drink.",
  rating="4.8 ★ (30 ratings)", flavor=["caramel", "smooth"])

R("coffee-float", "Iced Coffee Float", "over-ice",
  ("web", "Little Sugar Snaps (Elaine)", "https://www.littlesugarsnaps.com/wprm_print/coffee-float-iced-latte-with-ice-cream"),
  "iced", True, "quick", 4, "1 drink", "Tall heatproof glass",
  ["Ice", "Double shot of espresso (2 oz)", "Syrup of your choice (optional)", "Up to ½ cup (4 oz) milk", "1 scoop vanilla ice cream"],
  S("Double", "COLD-PRESSED"),
  espresso_steps("Double", "COLD-PRESSED", "the glass", cup_prep="Fill a tall heatproof glass with ice and add syrup if you like.") +
  ["Pour in the milk, leaving room at the top.", "Float a scoop of vanilla ice cream on top and serve with a long spoon."],
  note="Elaine brews hot espresso over the ice. COLD-PRESSED is smoother over ice and melts the ice cream less.",
  flavor=["dessert", "creamy"])

# ---------------- Cold Brew ----------------
R("chocolate-cream-cold-brew", "Chocolate Cream Cold Brew", "cold-brew",
  ("web", "CopyKat (Stephanie Manley)", "https://copykat.com/starbucks-chocolate-cream-cold-brew/"),
  "iced", True, "fancy", 8, "1 drink", "16 oz glass",
  ["Ice", "1 tbsp vanilla syrup", "8 oz cold brew", "Chocolate cream: 2 oz heavy cream, 1 oz 2% milk, 1 tbsp chocolate syrup, ½ tsp malt powder, 1 tsp sugar, tiny pinch of salt"],
  S("Luxe", "COLD BREW", 8, froth="COLD FOAM", milkType="DAIRY"),
  froth_steps("the heavy cream and milk", "COLD FOAM", extra="the chocolate syrup, malt powder, sugar and salt") +
  ["Keep the chocolate foam in the jug while you brew."] +
  coffee_steps("COLD BREW", 8, "the glass", cup_prep="Fill a 16 oz glass halfway with ice and add the vanilla syrup.") +
  ["Pour the chocolate cream foam over the top."],
  note="Stephanie blends a bigger batch of the foam (½ cup cream, ½ cup milk). This is half of it, sized for the frother.",
  rating="5.0 ★ (4 ratings)", flavor=["chocolate", "creamy"])

R("irish-cream-cold-brew", "Irish Cream Cold Brew", "cold-brew",
  ("web", "Feast + West (Jenny Park)", "https://feastandwest.com/irish-cream-cold-brew/"),
  "iced", True, "fancy", 10, "1 drink", "12 oz glass",
  ["Ice", "10 oz cold brew", "½ oz (1 tbsp) Irish cream syrup", "Cold foam: ½ cup heavy cream, 1 tbsp Irish cream liqueur or syrup, 1 tbsp sugar"],
  S("Luxe", "COLD BREW", 10, froth="COLD FOAM", milkType="DAIRY"),
  froth_steps("½ cup cold heavy cream", "COLD FOAM", extra="the Irish cream liqueur (or syrup) and sugar") +
  coffee_steps("COLD BREW", 10, "the glass", cup_prep="Fill a 12 oz glass with ice.") +
  ["Stir in the Irish cream syrup to taste, leaving an inch at the top.", "Spoon the foam over the top."],
  sub=[dict(name="Irish cream syrup (alcohol-free option)", ingredients=["½ cup sugar", "½ cup water", "¾ tsp unsweetened cocoa", "¾ tsp instant espresso powder", "1 tsp vanilla extract", "1 tsp Irish whiskey (optional)"],
            steps=["Heat the sugar and water until dissolved, then turn off the heat.", "Whisk in the cocoa and espresso powder, then the vanilla and whiskey.", "Strain into a jar. Keeps a month in the fridge."])],
  rating="5.0 ★ (53 ratings)", flavor=["creamy", "chocolate"])

R("brown-sugar-cold-brew", "Brown Sugar Cold Brew with Brown Sugar Foam", "cold-brew",
  ("web", "Food Network (Sunny Anderson)", "https://www.foodnetwork.com/recipes/sunny-anderson/sunnys-brown-sugar-cold-brew-coffee-with-brown-sugar-cold-foam-13326520"),
  "iced", True, "quick", 8, "1 drink", "16 oz glass",
  ["Ice", "1 tbsp brown sugar syrup", "10 oz cold brew", "¼ cup sweetened vanilla oat or almond milk, chilled", "1½ tsp dark brown sugar", "Cinnamon sugar, to dust"],
  S("Luxe", "COLD BREW", 10, froth="COLD FOAM", milkType="PLANT-BASED"),
  froth_steps("the chilled vanilla oat or almond milk (fill to the minimum line if needed)", "COLD FOAM", "PLANT-BASED", extra="the dark brown sugar") +
  coffee_steps("COLD BREW", 10, "the glass", cup_prep="Fill a 16 oz glass with ice and add the brown sugar syrup.") +
  ["Spoon the foam on top and dust with cinnamon sugar."],
  note="Sunny steeps a pitcher of cold brew overnight. The Pro's COLD BREW style makes one glass in minutes.",
  sub=[BROWN_SUGAR_SYRUP], flavor=["caramel", "warm spice"])

# ---------------- Classic ----------------
R("gingerbread-coffee", "Sweet & Spiced Gingerbread Coffee", "classic", SBX("sweet-spiced-gingerbread-coffee"),
  "hot", True, "quick", 4, "1 mug", "12 oz mug",
  ["½ tsp molasses", "2 tsp brown sugar, plus a sprinkle", "⅛ tsp ground cinnamon, plus a sprinkle", "8 oz brewed coffee", "4 oz whole milk"],
  S("Luxe", "CLASSIC", 8, froth="THICK FROTH", milkType="DAIRY"),
  ["Put the molasses, brown sugar and cinnamon in a 12 oz mug."] +
  coffee_steps("CLASSIC", 8, "the mug") +
  ["Stir until the molasses dissolves."] +
  froth_steps("4 oz cold whole milk (fill to the minimum line if needed)", "THICK FROTH") +
  ["Pour the frothed milk over the coffee and sprinkle with cinnamon and brown sugar."],
  note="Starbucks uses gingerbread-flavored pods. Plain beans work fine: the molasses and spice carry the flavor.",
  flavor=["warm spice", "sweet"])

R("maple-brown-sugar-coffee", "Maple Vanilla Brown Sugar Coffee", "classic", SBX("maple-vanilla-brown-sugar"),
  "hot", True, "quick", 4, "1 mug", "12 oz mug",
  ["8 oz brewed coffee", "1½ tbsp half-and-half", "2 tsp brown sugar", "¼ tsp vanilla extract", "1 tsp maple syrup (for plain beans)", "Whipped cream and cinnamon (optional)"],
  S("Luxe", "CLASSIC", 8),
  coffee_steps("CLASSIC", 8, "a 12 oz mug") +
  ["Stir in the half-and-half, brown sugar, vanilla and maple syrup.", "Top with whipped cream and a pinch of cinnamon if you like."],
  note="Starbucks brews maple pecan flavored pods. With regular beans, the teaspoon of maple syrup brings the maple back.",
  flavor=["maple", "sweet"])

R("hot-buttered-coffee", "Hot Buttered Coffee", "classic", ("web", "Taste of Home", "https://www.tasteofhome.com/recipes/hot-buttered-coffee/"),
  "hot", False, "quick", 3, "1 mug (mix for 20)", "10 oz mug",
  ["1 tbsp spiced butter mix", "8 oz brewed coffee (dark roast)", "Cinnamon stick and whipped cream (optional)"],
  S("Luxe", "RICH", 8),
  ["Put 1 tbsp of the spiced butter mix in a 10 oz mug."] +
  coffee_steps("RICH", 8, "the mug") +
  ["Stir until the butter melts. Add a cinnamon stick and whipped cream if you like."],
  note="Taste of Home calls for a dark roast, so we brew on RICH. Keep it in the Classic list since it's an everyday mug.",
  sub=[dict(name="Spiced butter mix (makes 20)", ingredients=["1 cup packed brown sugar", "¼ cup butter, softened", "1 tsp vanilla extract", "½ tsp ground cinnamon", "¼ tsp ground nutmeg", "¼ tsp ground allspice", "⅛ tsp ground cloves"],
            steps=["Mix everything until smooth.", "Keep in an airtight container in the fridge for up to 2 weeks."])],
  flavor=["buttery", "warm spice"])

R("spiced-coffee", "Spiced Coffee", "classic", ("web", "Taste of Home", "https://www.tasteofhome.com/recipes/spiced-coffee/"),
  "hot", False, "quick", 5, "1 mug", "12 oz mug",
  ["2 tsp sugar", "1½ tsp chocolate syrup", "1 small drop anise extract (about ⅛ tsp, or to taste)", "1 cinnamon stick", "2 whole cloves", "8 oz brewed coffee"],
  S("Luxe", "CLASSIC", 8),
  ["Put the sugar, chocolate syrup, anise, cinnamon stick and cloves in a 12 oz mug."] +
  coffee_steps("CLASSIC", 8, "the mug") +
  ["Stir and let it steep 3 to 4 minutes, then lift out the cloves. Keep the cinnamon stick in as a stirrer."],
  note="Taste of Home slow-cooks 8 cups for 2 hours. This is one mug, steeped right in the cup.",
  flavor=["warm spice", "chocolate"])

# ---------------- Rich ----------------
R("peppermint-mocha", "Peppermint Mocha", "rich", ("web", "Bigger Bolder Baking (Gemma Stafford)", "https://www.biggerbolderbaking.com/starbucks-peppermint-mocha/"),
  "hot", True, "quick", 5, "1 mug", "14 oz mug",
  ["1 oz (30 g) bittersweet chocolate, chopped", "8 oz rich coffee", "½ cup (4 oz) milk", "⅛ tsp peppermint extract", "Whipped cream and crushed candy canes"],
  S("Luxe", "RICH", 8, froth="STEAMED MILK", milkType="DAIRY"),
  ["Put the chopped chocolate in a 14 oz mug."] +
  coffee_steps("RICH", 8, "the mug") +
  ["Stir until the chocolate melts."] +
  froth_steps("½ cup cold milk (fill to the minimum line if needed)", "STEAMED MILK") +
  ["Stir the milk and peppermint extract into the mug. Top with whipped cream and crushed candy canes."],
  note="Gemma simmers everything in a pan for 2 minutes. Hot RICH coffee melts the chocolate and STEAMED MILK heats the milk.",
  rating="4.65 ★ (113 ratings)", flavor=["chocolate", "minty"])

R("maple-cream-coffee", "Maple Cream Coffee", "rich", ("web", "Taste of Home", "https://www.tasteofhome.com/recipes/maple-cream-coffee/"),
  "hot", True, "quick", 4, "1 mug", "10 oz mug",
  ["6 tbsp half-and-half", "2 tbsp maple syrup", "5 oz rich coffee", "2 tbsp whipped cream"],
  S("Luxe", "RICH", 6, froth="STEAMED MILK", milkType="DAIRY"),
  froth_steps("the half-and-half (fill to the minimum line if needed)", "STEAMED MILK", extra="the maple syrup") +
  ["Pour the warm maple cream into a 10 oz mug."] +
  coffee_steps("RICH", 6, "the mug") +
  ["Stir and top with whipped cream."],
  note="Taste of Home warms the cream and syrup in a pan and makes 2 cups. This is one cup.",
  flavor=["maple", "creamy"])

# ======================================================================
# short descriptions (recipes/blurbs.py)
from blurbs import BLURBS
_ids = {r["id"] for r in RECIPES}
assert not (_ids - set(BLURBS)), ("missing blurb", sorted(_ids - set(BLURBS)))
assert not (set(BLURBS) - _ids), ("blurb for unknown id", sorted(set(BLURBS) - _ids))
for r in RECIPES:
    r["blurb"] = BLURBS[r["id"]]

# duplicate check
# ======================================================================
def norm(s):
    s = s.lower()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return re.sub(r"\s+", " ", s).strip()

def signature(r):
    st = r["settings"]
    core = [norm(i) for i in r["ingredients"]]
    keys = sorted(set(w for i in core for w in i.split() if len(w) > 3))
    return (r["category"], st.get("style"), st.get("froth"), tuple(keys))

def check(recipes):
    ids, names, sigs, problems = {}, {}, {}, []
    for r in recipes:
        if r["id"] in ids: problems.append(f"duplicate id: {r['id']}")
        ids[r["id"]] = 1
        n = norm(r["name"])
        if n in names: problems.append(f"duplicate name: {r['name']} vs {names[n]}")
        names[n] = r["name"]
        sg = signature(r)
        if sg in sigs: problems.append(f"same drink twice: {r['name']} vs {sigs[sg]}")
        sigs[sg] = r["name"]
        cats = {c[0] for c in CATEGORIES}
        if r["category"] not in cats: problems.append(f"bad category on {r['id']}")
        if not r["steps"] or not r["ingredients"]: problems.append(f"empty recipe {r['id']}")
    return problems

if __name__ == "__main__":
    probs = check(RECIPES)
    if probs:
        print("DUPLICATE CHECK FAILED:"); [print(" -", p) for p in probs]; sys.exit(1)
    out = dict(categories=[dict(id=a, name=b, blurb=c) for a, b, c in CATEGORIES], recipes=RECIPES)
    p = pathlib.Path(__file__).with_name("recipes.json")
    p.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    from collections import Counter
    c = Counter((r["category"], r["source"]["kind"]) for r in RECIPES)
    for cid, cname, _ in CATEGORIES:
        print(f"{cname:15} ninja={c[(cid,'ninja')]:2}  outside={c[(cid,'web')]:2}")
    print("total", len(RECIPES), "-> duplicate check passed")

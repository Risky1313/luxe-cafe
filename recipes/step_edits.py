"""Step rewrites applied after the recipes are built (David's feedback, 2026-11-22):
- put sweeteners and mix-ins in the cup BEFORE pressing START BREW so they mix while it brews, then stir again
- start fully optional steps with "Optional:" (the site shows it as a tag); "(optional)" inside a step shows the same tag
Each entry: recipe id -> list of (exact old step, new step or list of steps)."""

EDITS = {
# mix-ins in the cup before brewing
"maple-brown-sugar-coffee": [
    ("Place a 12 oz mug under the spout and press START BREW.",
     ["Put the half-and-half, brown sugar, vanilla and maple syrup in a 12 oz mug.",
      "Place the mug under the spout and press START BREW. The coffee mixes everything as it brews."]),
    ("Stir in the half-and-half, brown sugar, vanilla and maple syrup.", "Stir well once it finishes."),
    ("Top with whipped cream and a pinch of cinnamon if you like.", "Optional: top with whipped cream and a pinch of cinnamon."),
],
"iced-lungo-macchiato": [
    ("Place a cup under the spout and press START BREW.", "Put the brown sugar in a cup, place it under the spout and press START BREW."),
    ("Stir in the brown sugar.", "Stir until the sugar dissolves."),
    ("Dust with chocolate powder if you like.", "Optional: dust with chocolate powder."),
],
"cold-brew-salted-honey-foam": [
    ("Fill a 16 oz glass with ice.", "Fill a 16 oz glass with ice and add about half the honey syrup."),
    ("Stir in about half the honey syrup.", "Stir to mix in the honey."),
],
"iced-cinnamon-honey-coffee": [
    ("Fill a 16 oz glass with ice.", "Fill a 16 oz glass with ice and add some cinnamon honey syrup."),
    ("Add a splash of milk and some cinnamon honey syrup, stir, and adjust to taste.", "Add a splash of milk, stir, and add more syrup to taste."),
],
"spiced-americano": [
    ("Place a 6 to 8 oz cup under the spout and press START BREW.", "Put 2 tbsp spiced syrup in a 6 to 8 oz cup, place it under the spout and press START BREW."),
    ("Add 2 oz hot water from the hot water spout and 2 tbsp spiced syrup, and stir.", "Add 2 oz hot water from the hot water spout and stir."),
],
"london-fog": [
    ("Put the tea bags in an 8 oz mug.", "Put the tea bags and sugar in an 8 oz mug."),
    ("Steep for 5 minutes, then remove the tea bags and stir in the sugar.", "Steep for 5 minutes, then remove the tea bags and stir."),
    ("Pour most of the milk into the tea, stir in the cream and vanilla, then add the last of the milk and foam.",
     ["Pour most of the milk into the tea, then add the last of the milk and foam.",
      "Optional: stir in the cream and vanilla before the last of the foam."]),
],
"hot-toddy": [
    ("Place a mug under the hot water spout.", "Put 2 tsp honey in a mug and place it under the hot water spout."),
    ("Add the whiskey, 2 tsp honey and 2 tsp lemon juice and stir until the honey dissolves.", "Add the whiskey and 2 tsp lemon juice and stir until the honey dissolves."),
    ("Garnish with a lemon round and a cinnamon stick.", "Garnish with a lemon round. Optional: add a cinnamon stick."),
],
"medicine-ball": [
    ("Put both tea bags in a large mug.", "Put both tea bags and the honey in a large mug."),
    ("Remove the tea bags, stir in the honey and the warm lemonade.", "Remove the tea bags and stir in the warm lemonade."),
],
# optional steps
"ristretto-over-ice": [("Add a few slices of fresh ginger if you like.", "Optional: add a few slices of fresh ginger.")],
"iced-lungo": [("Put 3 ice cubes and the sugar (if using) in a cocktail shaker.", "Put 3 ice cubes and the sugar (optional) in a cocktail shaker.")],
"americano-con-crema": [("Top with a few spoonfuls of the milk foam and sprinkle with sugar if you like.", "Top with a few spoonfuls of the milk foam. Optional: sprinkle with sugar.")],
"sparkling-long-black": [("Add the coconut syrup if you like.", "Optional: add the coconut syrup.")],
"espresso-martini": [("Float 3 espresso beans on top.", "Optional: float 3 espresso beans on top.")],
"stockholm-spice": [("Put the cinnamon, nutmeg, clove and sugar (if using) in the cup. Or tie the spices in a paper tea filter for a cleaner cup.",
                     "Put the cinnamon, nutmeg, clove and sugar (optional) in the cup. Or tie the spices in a paper tea filter for a cleaner cup.")],
"cinnamon-mocha-coffee": [("Add a cinnamon stick and whipped cream if you like.", "Optional: add a cinnamon stick and whipped cream.")],
"creamy-hot-cocoa": [("Top with whipped cream if you like.", "Optional: top with whipped cream.")],
"hot-buttered-coffee": [("Stir until the butter melts. Add a cinnamon stick and whipped cream if you like.",
                         ["Stir until the butter melts.", "Optional: add a cinnamon stick and whipped cream."])],
"einspanner": [("Stir in 2 tbsp hot water if you'd like it a little longer.", "Optional: stir in 2 tbsp hot water for a slightly longer drink."),
               ("Finish with chocolate shavings or cocoa and serve right away.", ["Optional: finish with chocolate shavings or cocoa.", "Serve right away."])],
"iced-americano": [("Taste, then add up to 2 tbsp cold water if you want it milder.", "Optional: taste, then add up to 2 tbsp cold water for a milder drink.")],
"lavender-latte": [("Pour the milk into the center of the espresso, finishing with foam. Scatter a few lavender buds on top.",
                    ["Pour the milk into the center of the espresso, finishing with foam.", "Optional: scatter a few lavender buds on top."])],
"salted-caramel-apple-coffee": [("Add the milk, then top with whipped cream, caramel, cinnamon or a rolled wafer cookie.",
                                 ["Add the milk and stir.", "Optional: top with whipped cream, caramel, cinnamon or a rolled wafer cookie."])],
"cafe-con-leche": [("Pour the espresso into the milk and stir until light brown. Taste, and add more sugar or a tiny pinch of salt if you like.",
                    "Pour the espresso into the milk and stir until light brown. Optional: add more sugar or a tiny pinch of salt to taste.")],
"coffee-float": [("Fill a tall heatproof glass with ice and add syrup if you like.", "Fill a tall heatproof glass with ice. Optional: add syrup.")],
}

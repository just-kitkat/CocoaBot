# BACKUP FOR UPGRADES COMMAND!!!
      img = Image.open("images/upgrade_farm_g.png").convert("RGBA")
      coins = "\U0001FA99"
      font = ImageFont.truetype('fonts/arial.ttf', 24)
      #draw = ImageDraw.Draw(img)
      
      with Pilmoji(img) as pilmoji:
        for upgrade in upgrades_map["farm"]:
          text = f"""
{upgrades[upgrade]['name']}
Income: {upgrades[upgrade]['income']} {coins} / hr
Cost: {upgrades[upgrade]['cost']} {coins}
"""
          pilmoji.text(upgrades[upgrade]["coords"], text.strip(), (0, 0, 0), font)
          
      # Save the image
      img.save("images/to_send.png")
  
      msg = ""
      
      file = discord.File("images/to_send.png", filename="temp.png")
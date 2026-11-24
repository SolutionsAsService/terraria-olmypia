using Microsoft.Xna.Framework;
using Terraria;
using Terraria.Audio;
using Terraria.GameContent.ItemDropRules;
using Terraria.ID;
using Terraria.ModLoader;

namespace Olympia.Items
{
    public class WingedSandals : ModItem
    {
        public override void SetDefaults()
        {
            Item.width = 36;
            Item.height = 30;
            Item.rare = ItemRarityID.Orange;
            Item.value = 60000;
            Item.accessory = true;
            Item.defense = 0;
        }

        public override void UpdateAccessory(Player player, bool hideVisual)
        {
            player.moveSpeed += 0.15f;
            player.accRunSpeed = 6.5f;
            player.jumpSpeedBoost += 1.2f;
        }
    }
}

using Microsoft.Xna.Framework;
using Terraria;
using Terraria.Audio;
using Terraria.GameContent.ItemDropRules;
using Terraria.ID;
using Terraria.ModLoader;

namespace Olympia.Items
{
    public class HellfangBlade : ModItem
    {
        public override void SetDefaults()
        {
            Item.width = 44;
            Item.height = 44;
            Item.rare = ItemRarityID.Orange;
            Item.value = 60000;
            Item.damage = 46;
            Item.DamageType = DamageClass.Melee;
            Item.useTime = 15;
            Item.useAnimation = 15;
            Item.useStyle = ItemUseStyleID.Swing;
            Item.knockBack = 5.0f;
            Item.UseSound = SoundID.Item1;
            Item.autoReuse = true;
        }

        public override void ModifyHitNPC(Player player, NPC target, ref NPC.HitModifiers modifiers)
        {
            if (false)
            {
                modifiers.FinalDamage *= 1.4f;
            }
        }

        public override void AddRecipes()
        {
            CreateRecipe().AddIngredient(ModContent.ItemType<Items.CerberusFang>(), 8).AddIngredient(ModContent.ItemType<Items.BronzeBar>(), 10).AddTile(TileID.Anvils).Register();
        }
    }
}

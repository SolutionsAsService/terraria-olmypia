using Microsoft.Xna.Framework;
using Terraria;
using Terraria.Audio;
using Terraria.GameContent.ItemDropRules;
using Terraria.ID;
using Terraria.ModLoader;

namespace Olympia.Items
{
    public class LernaeanBow : ModItem
    {
        public override void SetDefaults()
        {
            Item.width = 36;
            Item.height = 44;
            Item.rare = ItemRarityID.Lime;
            Item.value = 160000;
            Item.damage = 62;
            Item.DamageType = DamageClass.Ranged;
            Item.useTime = 14;
            Item.useAnimation = 14;
            Item.useStyle = ItemUseStyleID.Shoot;
            Item.noMelee = true;
            Item.knockBack = 3.0f;
            Item.UseSound = SoundID.Item5;
            Item.autoReuse = true;
            Item.shoot = ProjectileID.WoodenArrowFriendly;
            Item.shootSpeed = 17.0f;
            Item.useAmmo = AmmoID.Arrow;
        }

        public override void AddRecipes()
        {
            CreateRecipe().AddIngredient(ModContent.ItemType<Items.HydraScale>(), 14).AddIngredient(ModContent.ItemType<Items.BronzeBar>(), 8).AddTile(TileID.Anvils).Register();
        }
    }
}

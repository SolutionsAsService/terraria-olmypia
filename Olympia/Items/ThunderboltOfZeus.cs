using Microsoft.Xna.Framework;
using Terraria;
using Terraria.Audio;
using Terraria.GameContent.ItemDropRules;
using Terraria.ID;
using Terraria.ModLoader;

namespace Olympia.Items
{
    public class ThunderboltOfZeus : ModItem
    {
        public override void SetDefaults()
        {
            Item.width = 36;
            Item.height = 44;
            Item.rare = ItemRarityID.Red;
            Item.value = 500000;
            Item.damage = 176;
            Item.DamageType = DamageClass.Magic;
            Item.mana = 20;
            Item.noMelee = true;
            Item.useTime = 18;
            Item.useAnimation = 18;
            Item.useStyle = ItemUseStyleID.Shoot;
            Item.knockBack = 6.0f;
            Item.UseSound = SoundID.Item43;
            Item.autoReuse = true;
            Item.shoot = ModContent.ProjectileType<Projectiles.ThunderBolt>();
            Item.shootSpeed = 18.0f;
        }
    }
}

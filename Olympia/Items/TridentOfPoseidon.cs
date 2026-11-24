using Microsoft.Xna.Framework;
using Terraria;
using Terraria.Audio;
using Terraria.GameContent.ItemDropRules;
using Terraria.ID;
using Terraria.ModLoader;

namespace Olympia.Items
{
    public class TridentOfPoseidon : ModItem
    {
        public override void SetDefaults()
        {
            Item.width = 40;
            Item.height = 44;
            Item.rare = ItemRarityID.Lime;
            Item.value = 180000;
            Item.damage = 92;
            Item.DamageType = DamageClass.Magic;
            Item.mana = 14;
            Item.noMelee = true;
            Item.useTime = 22;
            Item.useAnimation = 22;
            Item.useStyle = ItemUseStyleID.Shoot;
            Item.knockBack = 5.0f;
            Item.UseSound = SoundID.Item43;
            Item.autoReuse = true;
            Item.shoot = ModContent.ProjectileType<Projectiles.PoseidonWave>();
            Item.shootSpeed = 13.0f;
        }
    }
}

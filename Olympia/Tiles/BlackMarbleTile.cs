using Microsoft.Xna.Framework;
using Terraria;
using Terraria.Audio;
using Terraria.GameContent.ItemDropRules;
using Terraria.ID;
using Terraria.ModLoader;

namespace Olympia.Tiles
{
    public class BlackMarbleTile : ModTile
    {
        public override void SetStaticDefaults()
        {
            Main.tileSolid[Type] = true;
            Main.tileMergeDirt[Type] = true;
            Main.tileBlockLight[Type] = true;
            AddMapEntry(new Color(52, 50, 62));
            DustType = DustID.Stone;
            HitSound = SoundID.Tink;
            MineResist = 3.0f;
            MinPick = 0;
        }
    }
}

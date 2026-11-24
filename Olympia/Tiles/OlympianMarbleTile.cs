using Microsoft.Xna.Framework;
using Terraria;
using Terraria.Audio;
using Terraria.GameContent.ItemDropRules;
using Terraria.ID;
using Terraria.ModLoader;

namespace Olympia.Tiles
{
    public class OlympianMarbleTile : ModTile
    {
        public override void SetStaticDefaults()
        {
            Main.tileSolid[Type] = true;
            Main.tileMergeDirt[Type] = true;
            Main.tileBlockLight[Type] = true;
            AddMapEntry(new Color(232, 230, 238));
            DustType = DustID.Stone;
            HitSound = SoundID.Tink;
            MineResist = 2.0f;
            MinPick = 0;
        }
    }
}

using System.IO;
using Microsoft.Xna.Framework;
using Terraria;
using Terraria.ModLoader;
using Terraria.ModLoader.IO;

namespace Olympia.Systems
{
    /// <summary>World state: which bosses have fallen, and where each generated structure stands (tile coordinates).</summary>
    public class OlympiaWorld : ModSystem
    {
        public static bool downedMinotaur;
        public static bool downedMedusa;
        public static bool downedZeus;
        public static Rectangle TempleOfOlympusArea;
        public static Rectangle LabyrinthOfTheMinotaurArea;

        public static bool InArea(Player player, Rectangle area)
        {
            return area.Width > 0 && area.Contains(player.Center.ToTileCoordinates());
        }

        public override void ClearWorld()
        {
            downedMinotaur = false;
            downedMedusa = false;
            downedZeus = false;
            TempleOfOlympusArea = Rectangle.Empty;
            LabyrinthOfTheMinotaurArea = Rectangle.Empty;
        }

        public override void SaveWorldData(TagCompound tag)
        {
            if (downedMinotaur) { tag["downedMinotaur"] = true; }
            if (downedMedusa) { tag["downedMedusa"] = true; }
            if (downedZeus) { tag["downedZeus"] = true; }
            tag["TempleOfOlympusX"] = TempleOfOlympusArea.X;
            tag["TempleOfOlympusY"] = TempleOfOlympusArea.Y;
            tag["TempleOfOlympusW"] = TempleOfOlympusArea.Width;
            tag["TempleOfOlympusH"] = TempleOfOlympusArea.Height;
            tag["LabyrinthOfTheMinotaurX"] = LabyrinthOfTheMinotaurArea.X;
            tag["LabyrinthOfTheMinotaurY"] = LabyrinthOfTheMinotaurArea.Y;
            tag["LabyrinthOfTheMinotaurW"] = LabyrinthOfTheMinotaurArea.Width;
            tag["LabyrinthOfTheMinotaurH"] = LabyrinthOfTheMinotaurArea.Height;
        }

        public override void LoadWorldData(TagCompound tag)
        {
            downedMinotaur = tag.ContainsKey("downedMinotaur");
            downedMedusa = tag.ContainsKey("downedMedusa");
            downedZeus = tag.ContainsKey("downedZeus");
            TempleOfOlympusArea = new Rectangle(tag.GetInt("TempleOfOlympusX"), tag.GetInt("TempleOfOlympusY"), tag.GetInt("TempleOfOlympusW"), tag.GetInt("TempleOfOlympusH"));
            LabyrinthOfTheMinotaurArea = new Rectangle(tag.GetInt("LabyrinthOfTheMinotaurX"), tag.GetInt("LabyrinthOfTheMinotaurY"), tag.GetInt("LabyrinthOfTheMinotaurW"), tag.GetInt("LabyrinthOfTheMinotaurH"));
        }

        public override void NetSend(BinaryWriter writer)
        {
            writer.Write(downedMinotaur);
            writer.Write(downedMedusa);
            writer.Write(downedZeus);
            writer.Write(TempleOfOlympusArea.X);
            writer.Write(TempleOfOlympusArea.Y);
            writer.Write(TempleOfOlympusArea.Width);
            writer.Write(TempleOfOlympusArea.Height);
            writer.Write(LabyrinthOfTheMinotaurArea.X);
            writer.Write(LabyrinthOfTheMinotaurArea.Y);
            writer.Write(LabyrinthOfTheMinotaurArea.Width);
            writer.Write(LabyrinthOfTheMinotaurArea.Height);
        }

        public override void NetReceive(BinaryReader reader)
        {
            downedMinotaur = reader.ReadBoolean();
            downedMedusa = reader.ReadBoolean();
            downedZeus = reader.ReadBoolean();
            TempleOfOlympusArea = new Rectangle(reader.ReadInt32(), reader.ReadInt32(), reader.ReadInt32(), reader.ReadInt32());
            LabyrinthOfTheMinotaurArea = new Rectangle(reader.ReadInt32(), reader.ReadInt32(), reader.ReadInt32(), reader.ReadInt32());
        }
    }
}

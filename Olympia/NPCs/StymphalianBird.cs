using Microsoft.Xna.Framework;
using Terraria;
using Terraria.Audio;
using Terraria.GameContent.ItemDropRules;
using Terraria.ID;
using Terraria.ModLoader;

namespace Olympia.NPCs
{
    public class StymphalianBird : ModNPC
    {
        public override void SetStaticDefaults()
        {
            Main.npcFrameCount[Type] = 4;
        }

        public override void SetDefaults()
        {
            NPC.width = 34;
            NPC.height = 28;
            NPC.damage = 22;
            NPC.defense = 3;
            NPC.lifeMax = 30;
            NPC.HitSound = SoundID.NPCHit1;
            NPC.DeathSound = SoundID.NPCDeath1;
            NPC.knockBackResist = 0.8f;
            NPC.value = 60.0f;
            NPC.aiStyle = NPCAIStyleID.Bat;
            AIType = NPCID.CaveBat;
            AnimationType = NPCID.CaveBat;
            NPC.noGravity = true;
        }

        public override float SpawnChance(NPCSpawnInfo spawnInfo)
        {
            if (Systems.OlympiaWorld.InArea(spawnInfo.Player, Systems.OlympiaWorld.TempleOfOlympusArea))
            {
                return 0.5f;
            }
            if (Systems.OlympiaWorld.InArea(spawnInfo.Player, Systems.OlympiaWorld.LabyrinthOfTheMinotaurArea))
            {
                return 0.4f;
            }
            return spawnInfo.Player.ZoneOverworldHeight ? 0.015f : 0f;
        }

        public override void ModifyNPCLoot(NPCLoot npcLoot)
        {
            npcLoot.Add(ItemDropRule.Common(ItemID.Feather, 3, 1, 2));
        }
    }
}

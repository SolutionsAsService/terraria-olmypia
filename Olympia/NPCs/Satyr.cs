using Microsoft.Xna.Framework;
using Terraria;
using Terraria.Audio;
using Terraria.GameContent.ItemDropRules;
using Terraria.ID;
using Terraria.ModLoader;

namespace Olympia.NPCs
{
    public class Satyr : ModNPC
    {
        public override void SetStaticDefaults()
        {
            Main.npcFrameCount[Type] = 3;
        }

        public override void SetDefaults()
        {
            NPC.width = 36;
            NPC.height = 52;
            NPC.damage = 20;
            NPC.defense = 4;
            NPC.lifeMax = 60;
            NPC.HitSound = SoundID.NPCHit1;
            NPC.DeathSound = SoundID.NPCDeath1;
            NPC.knockBackResist = 0.5f;
            NPC.value = 100.0f;
            NPC.aiStyle = NPCAIStyleID.Fighter;
            AIType = NPCID.Zombie;
            AnimationType = NPCID.Zombie;
        }

        public override float SpawnChance(NPCSpawnInfo spawnInfo)
        {
            if (Systems.OlympiaWorld.InArea(spawnInfo.Player, Systems.OlympiaWorld.TempleOfOlympusArea))
            {
                return 0.4f;
            }
            return spawnInfo.Player.ZoneForest ? 0.05f : 0f;
        }

        public override void ModifyNPCLoot(NPCLoot npcLoot)
        {
            npcLoot.Add(ItemDropRule.Common(ModContent.ItemType<Items.AmbrosiaFlower>(), 6, 1, 1));
        }
    }
}

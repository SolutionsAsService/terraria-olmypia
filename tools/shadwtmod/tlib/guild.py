"""guild: the Adventurer's Guild system for The Wilds Beyond (and any mod with a `guild.json`).

content/guild.json  {ranks, contracts, discoveries}  ->  Systems/GuildData.cs, Systems/GuildPlayer.cs, Systems/GuildGlobalNPC.cs
content/townnpcs.json                                 ->  NPCs/<Id>.cs   (a Town NPC: chat, a contract button or a clue button, a shop)
npcs with "ai": "critter"                             ->  NPCs/<Id>.cs   (a passive wanderer that counts as a journal discovery when observed)
item kinds "journal", "map", "artifact"               ->  Items/<Id>.cs

Rules the generated code keeps: no per-tick world scans (the discovery pass runs twice a second for the local player, over the 200 NPC slots, the inventory and a few
rectangles); one active contract at a time; every rank, reward and discovery is data; guild state lives on the ModPlayer and is saved with the character.
Not done in this slice: multiplayer sync of guild state (hunt credit is single-player only).
"""
import json
from .cs import HEAD, RARITY, f, item_ref, npc_ref, recipe_block, drops_rules


def q(s):
    return json.dumps(s, ensure_ascii=True)


def _coins(copper):
    plat, rest = divmod(copper, 1000000)
    gold, rest = divmod(rest, 10000)
    silver, cop = divmod(rest, 100)
    return plat, gold, silver, cop


def data_cs(g, structs_ids):
    ranks = g["ranks"]
    cons = []
    for c in g["contracts"]:
        tgt = ""
        if c["kind"] == "hunt":
            tgt = f"Target = {npc_ref(c['target'])}, "
        if c["kind"] == "collect":
            tgt = f"Item = {item_ref(c['item'])}, "
        rewards = ", ".join(f"new int[] {{ {item_ref(i)}, {n} }}" for i, n in c.get("reward", {}).get("items", []))
        cons.append(f"""                new ContractDef {{ Id = {q(c['id'])}, Name = {q(c['name'])}, Text = {q(c['text'])}, Done = {q(c['done'])}, Kind = {q(c['kind'])}, Rank = {c['rank']}, {tgt}Count = {c.get('count', 0)},
                    Category = {q(c.get('category', ''))}, Discovery = {q(c.get('discovery', ''))}, Rep = {c['rep']}, Copper = {c.get('reward', {}).get('copper', 0)}, After = {q(c.get('after', ''))},
                    Rewards = new int[][] {{ {rewards} }} }},""")
    ds, npcmap, itemmap, areamap = [], [], [], []
    for d in g["discoveries"]:
        ds.append(f"                new DiscoveryDef {{ Id = {q(d['id'])}, Name = {q(d['name'])}, Category = {q(d['category'])}, Rarity = {q(d.get('rarity', 'Common'))}, Text = {q(d['text'])} }},")
        if d.get("npc"):
            npcmap.append(f"            NpcDiscovery[ModContent.NPCType<NPCs.{d['npc']}>()] = {q(d['id'])};")
        if d.get("item"):
            itemmap.append(f"            ItemDiscovery[ModContent.ItemType<Items.{d['item']}>()] = {q(d['id'])};")
        if d.get("area"):
            areamap.append(f"            AreaDiscovery[{q(d['id'])}] = {q(d['area'])};")
    area_cases = "\n".join(f'                case "{a}": return KhemetWorld.{a}Area;' for a in structs_ids)
    return f"""using System;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using Terraria;
using Terraria.ID;
using Terraria.ModLoader;

namespace Khemet.Systems
{{
    public class ContractDef
    {{
        public string Id, Name, Text, Done, Kind, Category, Discovery, After;
        public int Rank, Count, Rep, Copper, Target, Item;
        public int[][] Rewards;
    }}

    public class DiscoveryDef
    {{
        public string Id, Name, Category, Rarity, Text;
    }}

    /// <summary>The guild's tables, generated from content/guild.json. Built on first use, because mod item and NPC types exist only after loading.</summary>
    public static class GuildData
    {{
        public static readonly string[] RankNames = {{ {", ".join(q(r['name']) for r in ranks)} }};
        public static readonly int[] RankRep = {{ {", ".join(str(r['rep']) for r in ranks)} }};
        public static ContractDef[] Contracts;
        public static DiscoveryDef[] Discoveries;
        public static Dictionary<int, string> NpcDiscovery = new Dictionary<int, string>();
        public static Dictionary<int, string> ItemDiscovery = new Dictionary<int, string>();
        public static Dictionary<string, string> AreaDiscovery = new Dictionary<string, string>();

        public static void Ensure()
        {{
            if (Contracts != null)
            {{
                return;
            }}
            Contracts = new ContractDef[]
            {{
{chr(10).join(cons)}
            }};
            Discoveries = new DiscoveryDef[]
            {{
{chr(10).join(ds)}
            }};
{chr(10).join(npcmap)}
{chr(10).join(itemmap)}
{chr(10).join(areamap)}
        }}

        public static Rectangle AreaOf(string name)
        {{
            switch (name)
            {{
{area_cases}
                default: return Rectangle.Empty;
            }}
        }}

        public static DiscoveryDef Find(string id)
        {{
            Ensure();
            foreach (DiscoveryDef d in Discoveries)
            {{
                if (d.Id == id)
                {{
                    return d;
                }}
            }}
            return null;
        }}

        public static ContractDef FindContract(string id)
        {{
            Ensure();
            foreach (ContractDef c in Contracts)
            {{
                if (c.Id == id)
                {{
                    return c;
                }}
            }}
            return null;
        }}

        /// <summary>A clue, not a coordinate: a direction and a rough distance in the owner's words, and what to look for.</summary>
        public static string Clue(Player player, string key)
        {{
            string area = key;
            Rectangle r = AreaOf(area);
            if (r.Width == 0)
            {{
                return "The map is blank. Whatever it showed is not in this world.";
            }}
            int dx = r.X + r.Width / 2 - (int)(player.Center.X / 16f);
            string dir = dx >= 0 ? "east" : "west";
            int d = Math.Abs(dx);
            string far = d < 150 ? "a short walk" : (d < 500 ? "a good day's walk" : "a long journey");
            return "Go " + dir + ", " + far + " from here. Keep to open ground, and look for stone that does not belong in the grass.";
        }}
    }}
}}
"""


def player_cs():
    return """using System.Collections.Generic;
using Microsoft.Xna.Framework;
using Terraria;
using Terraria.ID;
using Terraria.ModLoader;
using Terraria.ModLoader.IO;

namespace Khemet.Systems
{
    /// <summary>A character's guild record: reputation (which gives the rank), the journal, finished contracts and the one active contract. Saved with the character.</summary>
    public class GuildPlayer : ModPlayer
    {
        public int Rep;
        public HashSet<string> Discovered = new HashSet<string>();
        public HashSet<string> Completed = new HashSet<string>();
        public string Active = "";
        public int Progress;
        public bool Observe;
        private int tick;

        public override void ResetEffects()
        {
            Observe = false;
        }

        public override void SaveData(TagCompound tag)
        {
            tag["rep"] = Rep;
            tag["discovered"] = new List<string>(Discovered);
            tag["completed"] = new List<string>(Completed);
            tag["active"] = Active;
            tag["progress"] = Progress;
        }

        public override void LoadData(TagCompound tag)
        {
            Rep = tag.GetInt("rep");
            Discovered = new HashSet<string>(tag.GetList<string>("discovered"));
            Completed = new HashSet<string>(tag.GetList<string>("completed"));
            Active = tag.GetString("active");
            Progress = tag.GetInt("progress");
        }

        public int Rank()
        {
            int r = 0;
            for (int i = 0; i < GuildData.RankRep.Length; i++)
            {
                if (Rep >= GuildData.RankRep[i])
                {
                    r = i;
                }
            }
            return r;
        }

        public string RankName()
        {
            return GuildData.RankNames[Rank()];
        }

        /// <summary>Twice a second, for the local player only: observe wildlife nearby, notice artifacts in the pack, notice standing in a ruin. No tile scans.</summary>
        public override void PostUpdate()
        {
            if (Player.whoAmI != Main.myPlayer)
            {
                return;
            }
            tick++;
            if (tick % 30 != 0)
            {
                return;
            }
            GuildData.Ensure();
            float radius = Observe ? 560f : 300f;
            for (int i = 0; i < Main.maxNPCs; i++)
            {
                NPC n = Main.npc[i];
                if (n.active && GuildData.NpcDiscovery.TryGetValue(n.type, out string nid) && !Discovered.Contains(nid) && n.Distance(Player.Center) < radius)
                {
                    Discover(nid);
                }
            }
            if (tick % 60 == 0)
            {
                foreach (Item it in Player.inventory)
                {
                    if (!it.IsAir && GuildData.ItemDiscovery.TryGetValue(it.type, out string iid) && !Discovered.Contains(iid))
                    {
                        Discover(iid);
                    }
                }
            }
            foreach (KeyValuePair<string, string> kv in GuildData.AreaDiscovery)
            {
                if (!Discovered.Contains(kv.Key) && KhemetWorld.InArea(Player, GuildData.AreaOf(kv.Value)))
                {
                    Discover(kv.Key);
                }
            }
        }

        public void Discover(string id)
        {
            if (!Discovered.Add(id))
            {
                return;
            }
            DiscoveryDef d = GuildData.Find(id);
            Rep += 2;
            Main.NewText("Journal: " + (d != null ? d.Name + " (" + d.Category + ")" : id) + ". The guild notes your find.", 120, 220, 160);
        }

        public void OnKill(int npcType)
        {
            GuildData.Ensure();
            ContractDef c = GuildData.FindContract(Active);
            if (c != null && c.Kind == "hunt" && c.Target == npcType)
            {
                Progress++;
            }
        }

        public int Have(int itemType)
        {
            int n = 0;
            foreach (Item it in Player.inventory)
            {
                if (!it.IsAir && it.type == itemType)
                {
                    n += it.stack;
                }
            }
            return n;
        }

        private int CategoryCount(string category)
        {
            int n = 0;
            foreach (string id in Discovered)
            {
                DiscoveryDef d = GuildData.Find(id);
                if (d != null && d.Category == category)
                {
                    n++;
                }
            }
            return n;
        }

        public int Current(ContractDef c)
        {
            switch (c.Kind)
            {
                case "hunt": return Progress;
                case "collect": return Have(c.Item);
                case "discover": return Discovered.Contains(c.Discovery) ? 1 : 0;
                case "discover_count": return CategoryCount(c.Category);
                default: return 1;
            }
        }

        public int Needed(ContractDef c)
        {
            return c.Kind == "discover" || c.Kind == "talk" ? 1 : c.Count;
        }

        private ContractDef NextAvailable()
        {
            GuildData.Ensure();
            foreach (ContractDef c in GuildData.Contracts)
            {
                if (c.Rank - 1 <= Rank() && !Completed.Contains(c.Id) && (c.After == "" || Completed.Contains(c.After)))
                {
                    return c;
                }
            }
            return null;
        }

        private void Pay(ContractDef c)
        {
            if (c.Kind == "collect")
            {
                int left = c.Count;
                foreach (Item it in Player.inventory)
                {
                    if (left > 0 && !it.IsAir && it.type == c.Item)
                    {
                        int take = it.stack < left ? it.stack : left;
                        it.stack -= take;
                        left -= take;
                        if (it.stack <= 0)
                        {
                            it.TurnToAir();
                        }
                    }
                }
            }
            var src = Player.GetSource_GiftOrReward();
            int copper = c.Copper;
            if (copper >= 10000) { Player.QuickSpawnItem(src, ItemID.GoldCoin, copper / 10000); copper %= 10000; }
            if (copper >= 100) { Player.QuickSpawnItem(src, ItemID.SilverCoin, copper / 100); }
            foreach (int[] r in c.Rewards)
            {
                Player.QuickSpawnItem(src, r[0], r[1]);
            }
            Completed.Add(c.Id);
            Rep += c.Rep;
            Active = "";
            Progress = 0;
        }

        /// <summary>The Guild Master's "Contracts" button: turn in the active contract if it is done, show its progress if not, or hand out the next one this rank allows.</summary>
        public string Contracts()
        {
            GuildData.Ensure();
            ContractDef a = GuildData.FindContract(Active);
            if (a != null)
            {
                if (Current(a) >= Needed(a))
                {
                    int before = Rank();
                    Pay(a);
                    string up = Rank() > before ? " You are now a " + RankName() + "." : "";
                    return a.Done + " (+" + a.Rep + " reputation)." + up;
                }
                return a.Name + ": " + a.Text + " [" + Current(a) + "/" + Needed(a) + "]";
            }
            ContractDef next = NextAvailable();
            if (next == null)
            {
                return "Nothing on the board that suits a " + RankName() + " right now. Go and see something new, and the board will change.";
            }
            Active = next.Id;
            Progress = 0;
            if (next.Kind == "talk")
            {
                return Contracts();
            }
            return "New contract, " + next.Name + ": " + next.Text;
        }

        /// <summary>The journal, as chat lines: the rank and reputation, then each category with what is found of what is known.</summary>
        public List<string> JournalLines()
        {
            GuildData.Ensure();
            var lines = new List<string>();
            int next = Rank() + 1 < GuildData.RankRep.Length ? GuildData.RankRep[Rank() + 1] : -1;
            lines.Add("Guild rank: " + RankName() + " (" + Rep + (next >= 0 ? "/" + next : "") + " reputation).");
            var cats = new List<string>();
            foreach (DiscoveryDef d in GuildData.Discoveries)
            {
                if (!cats.Contains(d.Category))
                {
                    cats.Add(d.Category);
                }
            }
            foreach (string cat in cats)
            {
                int have = 0, all = 0;
                var names = new List<string>();
                foreach (DiscoveryDef d in GuildData.Discoveries)
                {
                    if (d.Category != cat)
                    {
                        continue;
                    }
                    all++;
                    if (Discovered.Contains(d.Id))
                    {
                        have++;
                        names.Add(d.Name);
                    }
                }
                lines.Add(cat + " " + have + "/" + all + (names.Count > 0 ? ": " + string.Join(", ", names) : ""));
            }
            ContractDef a = GuildData.FindContract(Active);
            lines.Add(a != null ? "Active contract: " + a.Name + " [" + Current(a) + "/" + Needed(a) + "]" : "No active contract.");
            return lines;
        }
    }
}
"""


def global_npc_cs():
    return """using Terraria;
using Terraria.ID;
using Terraria.ModLoader;

namespace Khemet.Systems
{
    /// <summary>Hunt contracts count kills. Single-player only in this version: in multiplayer the server runs OnKill and guild state is not synced to clients.</summary>
    public class GuildGlobalNPC : GlobalNPC
    {
        public override void OnKill(NPC npc)
        {
            if (Main.netMode == NetmodeID.SinglePlayer)
            {
                Main.LocalPlayer.GetModPlayer<GuildPlayer>().OnKill(npc.type);
            }
        }
    }
}
"""


def town_npc_cs(spec):
    cls = spec["id"]
    quotes = spec["quotes"]
    pools = []
    for key in ("default", "night", "rank0", "rank1", "rank2"):
        vals = quotes.get(key, [])
        pools.append((key, vals))

    def lst(vals):
        return "new List<string> { " + ", ".join(q(v) for v in vals) + " }"
    shop = "\n".join(f"            shop.Add({item_ref(i)});" for i in spec.get("shop", []))
    role = spec["role"]
    button = spec.get("button", "Contracts" if role == "guild" else "Clue")
    click = ("Main.npcChatText = Main.LocalPlayer.GetModPlayer<Systems.GuildPlayer>().Contracts();" if role == "guild" else
             f"Main.npcChatText = Systems.GuildData.Clue(Main.LocalPlayer, {q(spec.get('clue_area', ''))});")
    spawn = "return true;" if role == "guild" else f"return NPC.AnyNPCs(ModContent.NPCType<{spec.get('after_npc', 'GuildMaster')}>());"
    names = ", ".join(q(n) for n in spec["names"])
    return f"""using System.Collections.Generic;
using Microsoft.Xna.Framework;
using Terraria;
using Terraria.ID;
using Terraria.ModLoader;

namespace Khemet.NPCs
{{
    [AutoloadHead]
    public class {cls} : ModNPC
    {{
        public override void SetStaticDefaults()
        {{
            Main.npcFrameCount[Type] = 25;
            NPCID.Sets.ExtraFramesCount[Type] = 9;
            NPCID.Sets.AttackFrameCount[Type] = 4;
            NPCID.Sets.DangerDetectRange[Type] = 700;
            NPCID.Sets.AttackType[Type] = 0;
            NPCID.Sets.AttackTime[Type] = 90;
            NPCID.Sets.AttackAverageChance[Type] = 30;
            NPCID.Sets.HatOffsetY[Type] = 4;
        }}

        public override void SetDefaults()
        {{
            NPC.townNPC = true;
            NPC.friendly = true;
            NPC.width = 18;
            NPC.height = 40;
            NPC.aiStyle = NPCAIStyleID.Passive;
            NPC.damage = 10;
            NPC.defense = 15;
            NPC.lifeMax = 250;
            NPC.HitSound = SoundID.NPCHit1;
            NPC.DeathSound = SoundID.NPCDeath1;
            NPC.knockBackResist = 0.5f;
            AnimationType = NPCID.Guide;
        }}

        public override bool CanTownNPCSpawn(int numTownNPCs)
        {{
            {spawn}
        }}

        public override List<string> SetNPCNameList()
        {{
            return new List<string> {{ {names} }};
        }}

        public override string GetChat()
        {{
            var pool = new List<string>();
            int rank = Main.LocalPlayer.GetModPlayer<Systems.GuildPlayer>().Rank();
            pool.AddRange({lst(pools[0][1])});
            if (!Main.dayTime)
            {{
                pool.AddRange({lst(pools[1][1])});
            }}
            if (rank == 0) {{ pool.AddRange({lst(pools[2][1])}); }}
            if (rank == 1) {{ pool.AddRange({lst(pools[3][1])}); }}
            if (rank >= 2) {{ pool.AddRange({lst(pools[4][1])}); }}
            return pool[Main.rand.Next(pool.Count)];
        }}

        public override void SetChatButtons(ref string button, ref string button2)
        {{
            button = {q(button)};
            button2 = "Shop";
        }}

        public override void OnChatButtonClicked(bool firstButton, ref string shopName)
        {{
            if (firstButton)
            {{
                {click}
            }}
            else
            {{
                shopName = "Shop";
            }}
        }}

        public override void AddShops()
        {{
            var shop = new NPCShop(Type, "Shop");
{shop}
            shop.Register();
        }}

        public override void TownNPCAttackStrength(ref int damage, ref float knockback)
        {{
            damage = 18;
            knockback = 3f;
        }}

        public override void TownNPCAttackCooldown(ref int cooldown, ref int randExtraCooldown)
        {{
            cooldown = 30;
            randExtraCooldown = 30;
        }}

        public override void TownNPCAttackProj(ref int projType, ref int attackDelay)
        {{
            projType = ProjectileID.WoodenArrowFriendly;
            attackDelay = 1;
        }}

        public override void TownNPCAttackProjSpeed(ref float multiplier, ref float gravityCorrection, ref float randomOffset)
        {{
            multiplier = 12f;
            randomOffset = 0.5f;
        }}
    }}
}}
"""


def critter_cs(spec):
    cls = spec["id"]
    size = spec["size"]
    sp = spec.get("spawn", {})
    zone = {"forest": "spawnInfo.Player.ZoneForest", "surface": "spawnInfo.Player.ZoneOverworldHeight", "any": "true"}.get(sp.get("zone", "forest"), "spawnInfo.Player.ZoneForest")
    night = "            if (Main.dayTime)\n            {\n                return 0f;\n            }\n" if sp.get("night") else ""
    return f"""{HEAD}
namespace Khemet.NPCs
{{
    /// <summary>A passive wanderer: it uses the vanilla bunny's AI and frame layout (seven frames), does no harm and is never hunted by the guild, only observed.</summary>
    public class {cls} : ModNPC
    {{
        public override void SetStaticDefaults()
        {{
            Main.npcFrameCount[Type] = 7;
            NPCID.Sets.CountsAsCritter[Type] = true;
        }}

        public override void SetDefaults()
        {{
            NPC.width = {size[0]};
            NPC.height = {size[1]};
            NPC.damage = 0;
            NPC.defense = 0;
            NPC.lifeMax = {spec.get('life', 8)};
            NPC.HitSound = SoundID.NPCHit1;
            NPC.DeathSound = SoundID.NPCDeath1;
            NPC.knockBackResist = 0.5f;
            NPC.friendly = true;
            NPC.aiStyle = NPCAIStyleID.Passive;
            AIType = NPCID.Bunny;
            AnimationType = NPCID.Bunny;
        }}

        public override float SpawnChance(NPCSpawnInfo spawnInfo)
        {{
{night}            return {zone} ? {f(sp.get('chance', 0.2))} : 0f;
        }}
    }}
}}
"""


def item_cs(spec):
    kind, cls = spec["kind"], spec["id"]
    size = spec.get("size", [28, 28])
    rare = RARITY[spec.get("rarity", "White")]
    common = f"            Item.width = {size[0]};\n            Item.height = {size[1]};\n            Item.rare = {rare};\n            Item.value = {int(spec.get('value', 0))};"
    if kind == "artifact":
        body = f"""        public override void SetStaticDefaults()
        {{
            Item.ResearchUnlockCount = 1;
        }}

        public override void SetDefaults()
        {{
{common}
            Item.maxStack = 1;
        }}"""
    elif kind == "journal":
        body = f"""        public override void SetDefaults()
        {{
{common}
            Item.useStyle = ItemUseStyleID.HoldUp;
            Item.useTime = 30;
            Item.useAnimation = 30;
            Item.UseSound = SoundID.Item1;
        }}

        public override bool? UseItem(Player player)
        {{
            if (player.whoAmI == Main.myPlayer)
            {{
                foreach (string line in player.GetModPlayer<Systems.GuildPlayer>().JournalLines())
                {{
                    Main.NewText(line, 230, 220, 160);
                }}
            }}
            return true;
        }}"""
    else:  # map
        body = f"""        public override void SetDefaults()
        {{
{common}
            Item.useStyle = ItemUseStyleID.HoldUp;
            Item.useTime = 30;
            Item.useAnimation = 30;
            Item.UseSound = SoundID.Item1;
        }}

        public override bool? UseItem(Player player)
        {{
            if (player.whoAmI == Main.myPlayer)
            {{
                Main.NewText({q(spec.get('map_text', 'A hand-drawn map.'))}, 230, 220, 160);
                Main.NewText(Systems.GuildData.Clue(player, {q(spec['clue_area'])}), 230, 220, 160);
            }}
            return true;
        }}"""
    return f"""{HEAD}
namespace Khemet.Items
{{
    public class {cls} : ModItem
    {{
{body}
{recipe_block(spec, cls)}    }}
}}
"""

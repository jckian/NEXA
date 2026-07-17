const fs = require('fs');
const files = [
  'c:/SCI-Arc/SP26-RESEARCH/programAgent/tpac-program-diagram.html', 
  'c:/SCI-Arc/SP26-RESEARCH/programAgent/references/TPAC-PROGRAM-DISTRIBUTION.txt'
];

for (const file of files) {
  if (!fs.existsSync(file)) {
    console.log("File not found:", file);
    continue;
  }
  let content = fs.readFileSync(file, 'utf8');

  // Fix TYPE_COLORS in HTML
  content = content.replace(
    /'restroom_female':\s+'#[0-9a-fA-F]+',\n\s*'restroom_male':\s+'#[0-9a-fA-F]+',\n\s*'accessible_restroom':\s+'#[0-9a-fA-F]+',/g,
    "'restroom':                       '#ffd07a',"
  );

  // Fix LEGEND_GROUPS in HTML
  content = content.replace(
    /'restroom_female',\s*'restroom_male',\s*'accessible_restroom',/g,
    "'restroom',"
  );

  // Fix defaultCluster in HTML
  content = content.replace(
    /const defaultCluster = \[\s*\{ type: 'restroom_female'[^}]+\},\s*\{ type: 'restroom_male'[^}]+\},\s*\{ type: 'accessible_restroom'[^}]+\},\s*\];/g,
    "const defaultCluster = [\n      { type: 'restroom', area: 168, level: level, category: 'public', w: 10, d: 16.8 },\n    ];"
  );
  
  // Fix restroomTypes Set
  content = content.replace(
    /const restroomTypes = new Set\(\['toilets','restroom_female','restroom_male','accessible_restroom'\]\);/g,
    "const restroomTypes = new Set(['toilets','restroom']);"
  );

  // In FLOOR_DATA or TXT file: just find and replace occurrences globally to change their string type.
  // Then we will have three `{restroom}` lines per cluster, which is fine, they just draw adjacent.
  // Wait, if it's fine to keep them adjacent (like three stall zones of the same overall logic), that's easiest.
  // Actually the user says "把三種RESTROOM合併", so merging their areas would be better but string replacement at least merges their type. let's just do type strings first.
  content = content.replace(/restroom_female/g, 'restroom');
  content = content.replace(/restroom_male/g, 'restroom');
  content = content.replace(/accessible_restroom/g, 'restroom');

  fs.writeFileSync(file, content);
  console.log('Processed:', file);
}

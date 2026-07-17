const fs = require('fs');

function updateHtml() {
    const file = 'c:/SCI-Arc/SP26-RESEARCH/programAgent/tpac-program-diagram.html';
    if (!fs.existsSync(file)) return;
    let content = fs.readFileSync(file, 'utf8');

    content = content.replace(/value="3\.5"/g, 'value="4.5"');
    content = content.replace(/\|\| 3\.5;/g, '|| 4.5;');
    content = content.replace(/floorHeight:\s*3\.5/g, 'floorHeight: 4.5');
    // Just to be sure PILOTIS remains 6
    content = content.replace(/const PILOTIS_H\s*=\s*[\d.]+;/g, 'const PILOTIS_H = 6.0;');

    fs.writeFileSync(file, content);
    console.log('HTML updated.');
}

function updateTxt() {
    const file = 'c:/SCI-Arc/SP26-RESEARCH/programAgent/references/TPAC-PROGRAM-DISTRIBUTION.txt';
    if (!fs.existsSync(file)) return;
    let content = fs.readFileSync(file, 'utf8');

    // Change top header
    content = content.replace(/Floor-to-floor: 3\.5m/g, 'Floor-to-floor: 4.5m');

    // Recalculate heights for headers
    // The pilotis is 6m. 
    // L1 is +6. 
    // Function to calculate exact height: Base 6m + (level - 1) * 4.5
    function getLevelElevation(level) {
        if (level === -1) return '-4.5';
        if (level === 0) return '0';
        if (level === 1) return '6';
        return (6 + (level - 1) * 4.5).toString();
    }

    // Regex matches lines like: ## L2  +9.5 m   Shared BOH — dressing, rehearsal, backstage
    // Or ## B1  Basement  -4.5 m
    content = content.replace(/## (L\d+|B1).+?([+-][\d.]+) m(.*)/g, (match, levelStr, oldHeight, rest) => {
        let level = 0;
        if (levelStr === 'B1') level = -1;
        else if (levelStr.startsWith('L')) level = parseInt(levelStr.substring(1), 10);

        // We already know B1, L0, L1 remain same - WAIT, B1 was -4.5. Wait, if floor is 4.5m, then B1 is at -4.5m. That is correct.
        const newHeight = getLevelElevation(level);

        // reconstruct the pattern replacing the old height number.
        // match is the whole line
        // find the height substring and replace it
        return match.replace(oldHeight + ' m', (level > 0 ? '+' : '') + newHeight + ' m');
    });

    fs.writeFileSync(file, content);
    console.log('TXT updated.');
}

updateHtml();
updateTxt();

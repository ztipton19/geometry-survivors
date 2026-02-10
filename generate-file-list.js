const fs = require('fs');
const path = require('path');

function findExcalidrawFiles(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  
  list.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat && stat.isDirectory()) {
      // Skip node_modules and hidden folders
      if (!file.startsWith('.') && file !== 'node_modules') {
        results = results.concat(findExcalidrawFiles(filePath));
      }
    } else if (file.endsWith('.excalidraw')) {
      // Store relative path
      results.push(path.relative('.', filePath));
    }
  });
  
  return results;
}

function updateFileList() {
  const files = findExcalidrawFiles('.');
  fs.writeFileSync('files.json', JSON.stringify(files, null, 2));
  console.log(`Updated files.json with ${files.length} files`);
}

// Run once
updateFileList();

// Watch for changes
if (process.argv.includes('--watch')) {
  console.log('Watching for changes...');
  setInterval(updateFileList, 2000);
}

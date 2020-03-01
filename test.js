const reg = /(.*)【(.*)】|(.*)【(.*)|(.*)】(.*)/;
original = "233【】】】1232】"
original = original.replace(/[【】]/g, "")
// original = original.replace(/【/g, "")
console.log(original)
let matchres = original.match(reg);

// if (matchres && matchres.length > 0) matchres = matchres.filter(a => a && a.trim());
// if (matchres && matchres.length > 1) matchres = matchres.splice(1);
console.log(matchres);
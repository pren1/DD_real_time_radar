const reg = /【(.*)】|【(.*)|(.*)】/;
original = "123】"
let matchres = original.match(reg);
console.log(matchres);
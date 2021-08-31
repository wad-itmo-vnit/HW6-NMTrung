// JavaScript source code
let galleryImages = document.querySelectorAll(".gallery img");
let getLastestOpenedImg;
let windowWidth = window.innerWidth;

if(galleryImages) {
	galleryImages.forEach(function(image, index) {
		image.onclick = function() {
			console.log(image.src);
			let getFullImgUrl = image.src;
			let getImgUrlPos = getFullImgUrl.split("/images/");
			let setNewImgUrl = getImgUrlPos[1]
			console.log(setNewImgUrl)
			getLastestOpenedImg = index + 1;

			let container = document.body;
			let newImgWindow = document.createElement("div");
			container.appendChild(newImgWindow);
			newImgWindow.setAttribute("class","img-window");
			newImgWindow.setAttribute("onclick","closeImg()");

			let newImg = document.createElement("img");
			newImgWindow.appendChild(newImg);
			newImg.setAttribute("src","/static/images/" + setNewImgUrl);
			newImg.setAttribute("id","current-img");



			newImg.onload = function(){
				let imgWidth = this.width;
				let calcImgToEdge = ((windowWidth - imgWidth)/2) - 80;

				let newNextBtn = document.createElement("a");
				let btnNextText = document.createTextNode("Next");
				newNextBtn.appendChild(btnNextText);
				container.appendChild(newNextBtn);
				newNextBtn.setAttribute("class","img-btn-next");
				newNextBtn.setAttribute("onclick", "changeImg(1)");
				newNextBtn.style.cssText = "right: " + (calcImgToEdge-15) + "px;";
	
				let newPrevBtn = document.createElement("a");
				let btnPrevText = document.createTextNode("Prev");
				newPrevBtn.appendChild(btnPrevText);
				container.appendChild(newPrevBtn);
				newPrevBtn.setAttribute("class","img-btn-prev");
				newPrevBtn.setAttribute("onclick", "changeImg(0)");
				newPrevBtn.style.cssText = "left: " + calcImgToEdge + "px;";
			}				
		}
	});
}

function closeImg(){
	document.querySelector(".img-window").remove();
	document.querySelector(".img-btn-next").remove();
	document.querySelector(".img-btn-prev").remove();
}

function changeImg(changeDir){
	document.querySelector("#current-img").remove();

	let getImgWindow = document.querySelector(".img-window");
	let newImg = document.createElement("img");
	getImgWindow.appendChild(newImg);

	let calcNewImg;
	if(changeDir === 1) {
		calcNewImg = getLastestOpenedImg + 1;
		if(calcNewImg > galleryImages.length) {
			calcNewImg = 1;
		}
	}

	else if(changeDir === 0){
		calcNewImg = getLastestOpenedImg - 1;
		if(calcNewImg < 1) {
			calcNewImg = galleryImages.length;
		}
	}

	newImg.setAttribute("src","/static/images/img" + calcNewImg + ".jpg");
	newImg.setAttribute("id","current-img");

	getLastestOpenedImg = calcNewImg;

	newImg.onload = function(){
		let imgWidth = this.width;
		let calcImgToEdge = ((windowWidth - imgWidth)/2) - 80;

		let nextBtn = document.querySelector(".img-btn-next");
		nextBtn.style.cssText = "right: " + (calcImgToEdge - 15) + "px;";

		let prevBtn = document.querySelector(".img-btn-prev");
		prevBtn.style.cssText = "left: " + calcImgToEdge + "px;";

	}
}
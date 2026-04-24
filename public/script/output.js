canvas.addEventListener('mouseup', async () => {
    document.getElementById("output").value += await sendData();
    clearCanvas();
});
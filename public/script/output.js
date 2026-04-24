canvas.addEventListener('mouseup', async () => {
    const out = await sendData();
    console.log(out)
    document.getElementById("output").value += out + ""
    clearCanvas();
});
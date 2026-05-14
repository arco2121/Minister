canvas.addEventListener('pointerup', async () => {
    const out = await sendData();
    console.log(out)
    document.getElementById("output").value += out + ""
    clearCanvas();
});
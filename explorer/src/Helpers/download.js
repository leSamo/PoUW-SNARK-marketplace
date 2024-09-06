export const downloadString = (filename, string) => {
    const element = document.createElement("a");
    const file = new Blob([string], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
}

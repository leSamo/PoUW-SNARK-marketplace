function padZero(num) {
    return num < 10 ? `0${num}` : num;
}

export const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = padZero(date.getMonth() + 1); // Months are 0-indexed
    const day = padZero(date.getDate());
    const hours = padZero(date.getHours());
    const minutes = padZero(date.getMinutes());
    
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

export const convertISOToLocalTime = (date) => {
  if (!date) return new Date();
  return new Date(date);
};

export const convertToISOString = (date) => {
  if (!date) return new Date().toISOString();
  const tzOffset = date.getTimezoneOffset() * 60000;
  const localDate = new Date(date.getTime() - tzOffset);
  return localDate.toISOString();
};

export const formatDateTimeSR = (date, options = {}) => {
  if (!date) return "";
  const defaultOptions = {
    timeZone: "Europe/Belgrade",
    ...options,
  };
  return new Date(date).toLocaleString("sr-RS", defaultOptions);
};

export const formatFullDateTimeSR = (date) => {
  if (!date) return "";
  return formatDateTimeSR(date, {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export const compareDates = (date1, date2) => {
  const d1 = date1 ? new Date(date1) : new Date();
  const d2 = date2 ? new Date(date2) : new Date();
  return d1.getTime() - d2.getTime();
};

export const isSameDay = (date1, date2) => {
  if (!date1 || !date2) return false;
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  return (
    d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate()
  );
};

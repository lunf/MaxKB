export function toThousands(num: any) {
  return num?.toString().replace(/\d+/, function (n: any) {
    return n.replace(/(\d)(?=(?:\d{3})+$)/g, '$1,')
  })
}
export function numberFormat(num: number) {
  return num < 1000 ? toThousands(num) : toThousands((num / 1000).toFixed(1)) + 'k'
}

export function filesize(size: number) {
  if (!size) return ''
  /* byte */
  const num = 1024.0

  if (size < num) return size + 'B'
  if (size < Math.pow(num, 2)) return (size / num).toFixed(2) + 'K' //kb
  if (size < Math.pow(num, 3)) return (size / Math.pow(num, 2)).toFixed(2) + 'M' //M
  if (size < Math.pow(num, 4)) return (size / Math.pow(num, 3)).toFixed(2) + 'G' //G
  return (size / Math.pow(num, 4)).toFixed(2) + 'T' //T
}

/*
  randomlyid
*/
export const randomId = function () {
  return Math.floor(Math.random() * 10000) + ''
}

/*
  Obtaining the documents.
*/
export function fileType(name: string) {
  const suffix = name.split('.')
  return suffix[suffix.length - 1]
}

/*
  Obtaining documents matching images
*/
export function getImgUrl(name: string) {
  const type = isRightType(name) ? fileType(name) : 'unknow'
  return new URL(`../assets/${type}-icon.svg`, import.meta.url).href
}
// Is it a white list?
export function isRightType(name: string) {
  const typeList = ['txt', 'pdf', 'docx', 'csv', 'md']
  return typeList.includes(fileType(name))
}

/*
  Filter the corresponding object from the specified number group.
*/
export function relatedObject(list: any, val: any, attr: string) {
  const filterData: any = list.filter((item: any) => item[attr] === val)?.[0]
  return filterData || null
}

// ordered
export function arraySort(list: Array<string>, property: any, desc?: boolean) {
  return list.sort((a: any, b: any) => {
    return desc ? b[property] - a[property] : a[property] - b[property]
  })
}

// All properties in the object are empty.
export function isAllPropertiesEmpty(obj: object) {
  return Object.values(obj).every(
    (value) =>
      value === null || typeof value === 'undefined' || (typeof value === 'string' && !value)
  )
}

// A collection of character values in a group of objects.
export function getAttrsArray(array: Array<any>, attr: string) {
  return array.map((item) => {
    return item[attr]
  })
}

// Please and
export function getSum(array: Array<any>) {
  return array.reduce((total, item) => total + item, 0)
}

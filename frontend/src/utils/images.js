const MAXIMUM_SIDE = 1600

export async function resizeImage(file) {
  const bitmap = await createImageBitmap(file)
  const scale = Math.min(1, MAXIMUM_SIDE / Math.max(bitmap.width, bitmap.height))
  const canvas = document.createElement('canvas')
  canvas.width = Math.round(bitmap.width * scale)
  canvas.height = Math.round(bitmap.height * scale)
  canvas.getContext('2d').drawImage(bitmap, 0, 0, canvas.width, canvas.height)
  return canvas.toDataURL('image/jpeg', 0.8)
}

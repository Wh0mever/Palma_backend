// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-expect-error
import noImage from '@/assets/no-image.png'

interface ImageBlockProps {
  width: number
  height: number
  borderRadius?: number
  data: any
}

const ImageBlock = ({ width, height, borderRadius, data }: ImageBlockProps) => {
  return (
    <div
      style={{
        width: width,
        height: height,
        borderRadius: borderRadius,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundImage: `url(${data && data.image || noImage})`
      }}
    />
  )
}

export default ImageBlock
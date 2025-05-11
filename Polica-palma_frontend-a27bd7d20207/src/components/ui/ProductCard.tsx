// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-expect-error
import noImage from '@/assets/no-image.png'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {IProductItem} from '@/typing/interfaces.ts'

const ProductCard = ({ image, title, price, onClick, inStock, florist, isSending }: IProductItem) => {
  const { formatter } = useNumberFormatter()

  return (
    <div
      className={`w-full h-full p-2 flex flex-col gap-5 bg-neutral-200 rounded-xl dark:bg-neutral-900 cursor-pointer ${isSending ? 'pointer-events-none cursor-not-allowed opacity-60' : ''}`}
      onClick={() => {
        if (onClick) {
          onClick()
        }
      }}
    >
      <div
        className='w-full h-[190px] rounded-xl'
        style={{
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundImage: `url(${image ? image : noImage})`
        }}
      />

      <div className='flex flex-col items-start gap-1'>
        <h2 className='text-lg font-bold'>{title}</h2>
        {florist && <h3 className="font-bold">Флорист: {florist}</h3>}
        {price && <p className="text-md font-semibold text-neutral-700 dark:text-neutral-300">{formatter.format(price)} сум</p>}
        {inStock && <p className="text-sm mt-1 font-medium">Осталось: <span className="font-bold">{inStock}</span> шт</p>}
        {inStock === 0 || inStock === '0' && <p className="text-sm text-red-500">Недостаточно товаров!</p>}
      </div>
    </div>
  )
}

export default ProductCard
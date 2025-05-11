/* eslint-disable @typescript-eslint/no-explicit-any */
import DashboardLayout from "@/components/elements/DashboardLayout.tsx";
import { Link, useNavigate, useParams } from "react-router-dom";
import SearchItem from "@/components/items/SearchItem.tsx";
import { Button } from "@/components/ui/button.tsx";
import { useEffect, useState } from "react";
import ProductCard from "@/components/ui/ProductCard.tsx";
import { ScrollArea } from "@/components/ui/scroll-area.tsx";
import useAxiosPost from "@/hooks/useAxiosPost.ts";
import AddForm from "@/components/others/AddForm.tsx";
import { z } from "zod";
import SelectFormField from "@/components/others/SelectFormField.tsx";
import { SelectItem } from "@/components/ui/select.tsx";
import useNumberFormatter from "@/hooks/useNumberFormatter.ts";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import translatedData from "@/data/translatedData.ts";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog.tsx";
import formatDate from "@/helpers/formatDate.ts";
import NumberFormField from "@/components/others/NumberFormField.tsx";
import useNumberValue from "@/hooks/useNumberValue.ts";
import { ChevronLeft, Eye, ScanLine, Trash2, Undo2 } from "lucide-react";
import useAxiosPut from "@/hooks/useAxiosPut.ts";
import EditDialog from "@/components/others/EditDialog.tsx";
import convertToBase64 from "@/helpers/convertToBase64.ts";
import ImageFormField from "@/components/others/ImageFormField.tsx";
import ImageBlock from "@/components/others/ImageBlock.tsx";
import EditSectionSkeleton from "@/components/skeletons/EditSectionSkeleton.tsx";
import CategoriesSkeleton from "@/components/skeletons/CategoriesSkeleton.tsx";
import ProductsSkeleton from "@/components/skeletons/ProductsSkeleton.tsx";
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx";
import ErrorItem from "@/components/items/ErrorItem.tsx";
import useDeleteItem from "@/hooks/useDeleteItem.ts";
import getUrl from "@/config.ts";
import ReturnDialog from "@/components/others/ReturnDialog.tsx";
import getUserData from "@/helpers/getUserData.ts";
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx";
import { api } from "@/services/api.ts";

interface BouquetImage {
  myFile: string | any;
}

const BouquetsEditPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { userType } = getUserData();
  const { formatter } = useNumberFormatter();
  const { deleteItem, isDeleting } = useDeleteItem();
  const { data, isLoading } = api.useGetBouquetsQuery({ id: id });
  const { data: categoriesData, isLoading: categoriesLoading } =
    api.useGetCompositeCategoriesQuery("");
  const { data: materialsData, isLoading: materialsLoading } =
    api.useGetCompositeProductsQuery("");
  const {
    data: factoriesCategoriesData,
    isLoading: factoriesCategoriesLoading,
  } = api.useGetFactoriesCategoriesQuery("");
  const { data: salesTypesData, isLoading: salesTypesLoading } =
    api.useGetFactoriesSalesTypesQuery("");

  const { data: floristsData, isLoading: floristsLoading } =
    api.useGetFloristsQuery("");

  const initialSelectedCategory =
    localStorage.getItem("selectedCategory") || "";
  const [selectedCategory, setSelectedCategory] = useState(
    initialSelectedCategory
  );

  const initialSelectedFlorist = localStorage.getItem("selectedFlorist") || "";
  const [selectedFlorist] = useState(initialSelectedFlorist);

  const [searchValue, setSearchValue] = useState<string>("");
  const [itemID, setItemID] = useState<string>("");
  const [countValue, setCountValue] = useState<string>("");
  const [bouquetImage, setBouquetImage] = useState<BouquetImage>({
    myFile: "",
  });
  const [dataStatusError, setDataStatusError] = useState<boolean>(false);
  const [factoryItemID, setFactoryItemID] = useState<string>("");
  const { data: factoryItemsReturns } = api.useGetFactoriesReturnsQuery({
    id: id,
    factoryItemID: factoryItemID,
  });
  const [postData, { isLoading: statusPending }] = api.usePostDataMutation();

  const { numberValue, handleNumberChange, setNumberValue } = useNumberValue();
  const {
    numberValue: writeOffNumberValue,
    handleNumberChange: handleWriteOffNumberChange,
    setNumberValue: setWriteOffNumberValue,
  } = useNumberValue();

  const { success, form, onSubmit, pending, error } = useAxiosPost(
    {
      warehouse_product: z.string({
        required_error: "Пожалуйста, выберите продукт",
      }),
      count: z.string({
        required_error: "Пожалуйста, введите количество продукта",
      }),
    },
    {
      count: numberValue.replace(/\s/g, ""),
    },
    `api/factories/product-factories/${id}/items/`,
    ["Bouquets", "Factories", "Products"]
  );

  const {
    success: writeOffSuccess,
    form: writeOffForm,
    onSubmit: writeOffSubmit,
    pending: writeOffPending,
    error: writeOffError,
    errorText: writeOffErrorText,
  } = useAxiosPost(
    {
      write_off_count: z.string({
        required_error: "Пожалуйста, введите количество продукта",
      }),
    },
    {
      write_off_count: writeOffNumberValue.replace(/\s/g, ""),
    },
    `api/factories/product-factories/${id}/items/${itemID}/write-off-product/`,
    ["Bouquets", "Factories", "Products"]
  );

  const {
    success: dataSuccess,
    form: dataForm,
    onSubmit: dataSubmit,
    pending: dataPending,
  } = useAxiosPut(
    {
      category: z.string().optional(),
      sales_type: z.string().optional(),
      florist: z.string().optional(),
      image: z.string().optional(),
    },
    {
      image: bouquetImage.myFile,
    },
    `api/factories/product-factories`,
    id,
    ["Bouquets"]
  );

  const {
    form: countForm,
    onSubmit: countSubmit,
    success: countSuccess,
    pending: countPending,
  } = useAxiosPut(
    {
      count: z.string({
        required_error: "Пожалуйста, введите количество товара",
      }),
    },
    {
      count: countValue.replace(/\s/g, ""),
    },
    `api/factories/product-factories/${id}/items`,
    itemID,
    ["Bouquets", "Factories", "Products"]
  );

  useEffect(() => {
    localStorage.setItem("selectedCategory", selectedCategory);
  }, [selectedCategory]);

  useEffect(() => {
    localStorage.setItem("selectedFlorist", selectedFlorist);
  }, [selectedFlorist]);

  useEffect(() => {
    if (countSuccess || success || writeOffSuccess) {
      setCountValue("");
      setNumberValue("");
      setWriteOffNumberValue("");
    }
  }, [
    success,
    countSuccess,
    setNumberValue,
    writeOffSuccess,
    setWriteOffNumberValue,
  ]);

  const filteredMaterials =
    materialsData &&
    Array.isArray(materialsData) &&
    materialsData.filter((item) => {
      const categoryFilter =
        selectedCategory && selectedCategory
          ? String(item.category?.id) === selectedCategory
          : true;

      const floristFilter =
        selectedFlorist && selectedFlorist
          ? String(item.florist?.id) === selectedFlorist
          : true;

      const searchFilter =
        item.name?.toLowerCase().includes(searchValue.toLowerCase()) ||
        item.code?.includes(searchValue.toLowerCase());
      return categoryFilter && floristFilter && searchFilter;
    });

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const handleSearch = (e: any) => {
    const inputValue = e.target.value;
    setSearchValue(inputValue);
  };

  const handleFileUpload = async (e: any) => {
    const file = e.target.files[0];
    const base64 = await convertToBase64(file);
    setBouquetImage({ ...bouquetImage, myFile: base64 });
  };

  const changeStatus = async (status: string) => {
    try {
      await postData({
        url: `api/factories/product-factories/${id}/${status}/`,
        body: {},
        invalidatesTags: ["Bouquets", "Factories", "Products"],
      });
    } catch (e) {
      console.log("Status change error:", e);
    }
  };

  const handleCountChange = (e: any) => setCountValue(e);

  return (
    <>
      <DashboardLayout>
        {!isLoading && data ? (
          <>
            <div className="w-full flex flex-col xl:flex-row gap-16 xl:gap-6">
              <section className="xl:w-2/5 w-full">
                <div className="flex flex-col gap-6">
                  <Button
                    variant="outline"
                    className="w-44"
                    onClick={() => navigate(-1)}
                  >
                    <ChevronLeft className="mr-2 w-4 h-4" /> Вернуться назад
                  </Button>

                  <div
                    className={`flex flex-col gap-6 ${
                      userType !== "ADMIN" &&
                      userType !== "MANAGER" &&
                      userType !== "WAREHOUSE_MASTER" &&
                      userType !== "CRAFTER"
                        ? "opacity-60 pointer-events-none select-none"
                        : ""
                    }`}
                  >
                    <div className="flex flex-col gap-4">
                      <SearchItem
                        placeholder="Поиск материалов"
                        value={searchValue}
                        onChange={handleSearch}
                        hasntBtn
                      />

                      <div className="w-full pb-2 max-w-full min-w-[200px] sm:min-w-[500px] xl:max-w-[800px] flex items-center gap-1 overflow-x-auto">
                        {!categoriesLoading ? (
                          <>
                            <Button
                              onClick={() => setSelectedCategory("")}
                              className={
                                selectedCategory === ""
                                  ? "bg-neutral-600 dark:bg-neutral-300"
                                  : ""
                              }
                            >
                              Все товары
                            </Button>

                            {categoriesData &&
                              Array.isArray(categoriesData) &&
                              categoriesData.map((item) => (
                                <Button
                                  key={item.id}
                                  onClick={() =>
                                    setSelectedCategory(String(item.id))
                                  }
                                  className={
                                    selectedCategory === String(item.id)
                                      ? "bg-neutral-600 dark:bg-neutral-300"
                                      : ""
                                  }
                                >
                                  {item.name}
                                </Button>
                              ))}
                          </>
                        ) : (
                          <CategoriesSkeleton />
                        )}
                      </div>

                      {dataStatusError && (
                        <ErrorItem
                          title="Ошибка"
                          desc="Вы не можете добавить ингридиент если букет собран"
                        />
                      )}
                    </div>

                    <ScrollArea className="h-[620px]">
                      <div className="w-full pr-4 pb-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                        {!materialsLoading &&
                        filteredMaterials &&
                        Array.isArray(filteredMaterials) ? (
                          filteredMaterials.map((item) => (
                            <>
                              {!success ? (
                                <Dialog key={item.id}>
                                  <DialogTrigger
                                    onClick={
                                      data.status === "CREATED"
                                        ? () => null
                                        : () => {
                                            setDataStatusError(true);
                                            setTimeout(
                                              () => setDataStatusError(false),
                                              2500
                                            );
                                          }
                                    }
                                  >
                                    <ProductCard
                                      key={item.id}
                                      image={item.image}
                                      title={item.name}
                                      inStock={formatter.format(item.in_stock)}
                                    />
                                  </DialogTrigger>

                                  {data.status === "CREATED" && (
                                    <DialogContent>
                                      <DialogHeader>
                                        <DialogTitle>
                                          Добавить материал
                                        </DialogTitle>
                                      </DialogHeader>

                                      <AddForm
                                        form={form.control}
                                        onSubmit={onSubmit}
                                        success={success}
                                        successDesc="Товар успешно добавлен"
                                      >
                                        <SelectFormField
                                          control={form.control}
                                          name="warehouse_product"
                                          placeholder="Выберите материал со склада"
                                          label="Материал со склада"
                                        >
                                          {item &&
                                            item.warehouse_products &&
                                            Array.isArray(
                                              item.warehouse_products
                                            ) &&
                                            item.warehouse_products.map(
                                              (item: any, index: any) => (
                                                <SelectItem
                                                  key={item.id}
                                                  value={item.id.toString()}
                                                >
                                                  <div className="flex gap-1">
                                                    <p className="font-semibold">
                                                      №{++index}
                                                    </p>{" "}
                                                    |
                                                    <p>
                                                      Кол-во:{" "}
                                                      <span className="font-medium">
                                                        {formatter.format(
                                                          item.count
                                                        )}{" "}
                                                        шт
                                                      </span>
                                                    </p>{" "}
                                                    |
                                                    <p>
                                                      Цена:{" "}
                                                      <span className="font-medium">
                                                        {formatter.format(
                                                          item.sale_price
                                                        )}{" "}
                                                        сум
                                                      </span>
                                                    </p>{" "}
                                                    |
                                                    <p>
                                                      Дата:{" "}
                                                      <span className="font-medium">
                                                        {formatDate(
                                                          item.created_at
                                                        )
                                                          .toString()
                                                          .slice(0, -10)}
                                                      </span>
                                                    </p>
                                                  </div>
                                                </SelectItem>
                                              )
                                            )}
                                        </SelectFormField>
                                        <NumberFormField
                                          control={form.control}
                                          name="count"
                                          label="Количество"
                                          _value={numberValue}
                                          _onChange={handleNumberChange}
                                        />
                                        {error && (
                                          <p className="text-sm text-red-500">
                                            Недостаточно товаров!
                                          </p>
                                        )}

                                        <Button disabled={pending}>
                                          Добавить материал
                                        </Button>
                                      </AddForm>
                                    </DialogContent>
                                  )}
                                </Dialog>
                              ) : null}
                            </>
                          ))
                        ) : (
                          <ProductsSkeleton />
                        )}

                        {filteredMaterials &&
                          filteredMaterials.length === 0 && (
                            <p className="text-xl font-bold">
                              Материалы не найдены!
                            </p>
                          )}
                      </div>
                    </ScrollArea>
                  </div>
                </div>
              </section>

              <section className="w-full flex flex-col justify-between gap-4">
                <div className="flex flex-col gap-5">
                  <div className="flex flex-col gap-1">
                    {data.status === "CREATED" && (
                      <h2 className="text-xl font-semibold">
                        Название: <span className="font-bold">{data.name}</span>
                      </h2>
                    )}
                    {data.status === "CREATED" && userType !== "CRAFTER" ? (
                      <p className="text-xl font-semibold">
                        Флорист:{" "}
                        <span className="font-bold">
                          {data.florist?.first_name ||
                            data.florist?.username ||
                            "-"}
                        </span>
                      </p>
                    ) : null}
                  </div>

                  {data.status === "CREATED" ? (
                    <AddForm
                      form={dataForm}
                      onSubmit={dataSubmit}
                      success={dataSuccess}
                      successDesc="Успешно изменено"
                      notMT
                    >
                      <div className="flex flex-col sm:flex-row items-center gap-3">
                        <ImageBlock
                          width={120}
                          height={100}
                          borderRadius={10}
                          data={data}
                        />

                        <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-2">
                          <ReactSelectFormField
                            idData={factoriesCategoriesData}
                            isLoading={factoriesCategoriesLoading}
                            control={dataForm.control}
                            name="category"
                            placeholder={data.category?.name}
                            disabled={
                              userType !== "ADMIN" &&
                              userType !== "MANAGER" &&
                              userType !== "WAREHOUSE_MASTER" &&
                              userType !== "CRAFTER"
                            }
                          />
                          <ReactSelectFormField
                            isValue
                            valueData={salesTypesData}
                            isLoading={salesTypesLoading}
                            control={dataForm.control}
                            name="sales_type"
                            placeholder={translatedData(data.sales_type)}
                            disabled={
                              userType !== "ADMIN" &&
                              userType !== "MANAGER" &&
                              userType !== "WAREHOUSE_MASTER" &&
                              userType !== "CRAFTER"
                            }
                          />
                          {/* Add Florist */}
                          <ReactSelectFormField
                            idData={floristsData}
                            isLoading={floristsLoading}
                            control={dataForm.control}
                            name="florist"
                            placeholder={data.florist?.first_name}
                            disabled={
                              userType !== "ADMIN" &&
                              userType !== "MANAGER" &&
                              userType !== "CRAFTER"
                            }
                          />

                          <ImageFormField
                            form={dataForm.control}
                            name="image"
                            placeholder="Выберите изображение"
                            _value={bouquetImage.myFile}
                            _onChange={(e: any) => handleFileUpload(e)}
                          />
                        </div>

                        <Button type="submit" disabled={dataPending}>
                          Изменить
                        </Button>
                      </div>
                    </AddForm>
                  ) : (
                    <div className="flex items-center gap-5">
                      <ImageBlock
                        width={180}
                        height={150}
                        borderRadius={10}
                        data={data}
                      />

                      <div className="w-full flex flex-col">
                        <p className="text-sm sm:text-lg font-semibold">
                          Название:{" "}
                          <span className="font-bold">{data.name}</span>
                        </p>
                        <p className="max-w-[450px] text-sm sm:text-lg font-semibold flex items-center gap-3">
                          Категория:{" "}
                          <span className="font-bold">
                            {data.category?.name}
                          </span>
                        </p>
                        <p className="text-sm sm:text-lg font-semibold flex items-center gap-3">
                          Тип продажи:{" "}
                          <span className="font-bold">
                            {translatedData(data.sales_type)}
                          </span>
                        </p>
                        {userType !== "CRAFTER" ? (
                          <p className="text-sm sm:text-lg font-semibold flex items-center gap-3">
                            Флорист:{" "}
                            <span className="font-bold">
                              {data.florist?.first_name ||
                                data.florist?.username ||
                                "-"}
                            </span>
                          </p>
                        ) : null}
                        {data.status === "SOLD" && (
                          <>
                            <p className="text-sm sm:text-lg font-semibold">
                              Продал:{" "}
                              <span className="font-bold">
                                {data.sold_user?.first_name ||
                                  data.sold_user?.username ||
                                  "-"}
                              </span>
                            </p>
                            <Link
                              to={`/dashboard/order/orders/edit/${data.order?.id}`}
                              className="text-sm sm:text-lg font-semibold hover:underline"
                            >
                              Продажа #{data.order?.id}
                            </Link>
                          </>
                        )}

                        {data.status !== "WRITTEN_OFF" && (
                          <AddForm
                            form={dataForm}
                            onSubmit={dataSubmit}
                            success={dataSuccess}
                            successDesc="Успешно изменено"
                          >
                            <div className="w-full flex items-center gap-2">
                              <ImageFormField
                                form={dataForm.control}
                                name="image"
                                placeholder="Выберите изображение"
                                _value={bouquetImage.myFile}
                                _onChange={(e: any) => handleFileUpload(e)}
                              />

                              <Button type="submit">Изменить</Button>
                            </div>
                          </AddForm>
                        )}
                      </div>
                    </div>
                  )}

                  <div
                    className={`${
                      userType !== "ADMIN" &&
                      userType !== "MANAGER" &&
                      userType !== "WAREHOUSE_MASTER" &&
                      userType !== "CRAFTER"
                        ? "opacity-60 pointer-events-none select-none"
                        : ""
                    }`}
                  >
                    <ScrollArea className="h-[590px]">
                      {!isLoading ? (
                        <Table className="w-full">
                          <TableHeader>
                            <TableRow>
                              <TableHead>№</TableHead>
                              <TableHead>Материал</TableHead>
                              <TableHead>Количество</TableHead>
                              <TableHead>Сумма</TableHead>
                              {userType !== "WAREHOUSE_MASTER" && (
                                <TableHead>Себестоимость</TableHead>
                              )}
                              {data.status === "WRITTEN_OFF" && (
                                <TableHead>Количество возврата</TableHead>
                              )}
                            </TableRow>
                          </TableHeader>

                          <TableBody>
                            {data &&
                              data.items &&
                              Array.isArray(data.items) &&
                              data.items.map((item: any, index: any) => (
                                <TableRow key={item.id}>
                                  <TableCell>{++index}</TableCell>
                                  <TableCell>
                                    {item.warehouse_product?.product_name}
                                  </TableCell>
                                  <TableCell>
                                    {formatter.format(item.count)}
                                    {data.status === "CREATED" && (
                                      <EditDialog
                                        dialogTitle="Изменить количество"
                                        form={countForm}
                                        submit={countSubmit}
                                        success={countSuccess}
                                        successDesc="Количество успешно изменено"
                                        btnClassname="ml-6"
                                        onClick={() => setItemID(item.id)}
                                        pending={countPending}
                                      >
                                        <NumberFormField
                                          _value={countValue}
                                          _onChange={handleCountChange}
                                          control={countForm.control}
                                          name="count"
                                          label="Количество товара"
                                          placeholder="Введите новое количество товара"
                                        />

                                        {error && (
                                          <p className="text-sm text-red-500">
                                            Недостаточно товаров!
                                          </p>
                                        )}
                                      </EditDialog>
                                    )}
                                  </TableCell>
                                  <TableCell>
                                    {formatter.format(item.total_price)} сум
                                  </TableCell>
                                  {userType !== "WAREHOUSE_MASTER" && (
                                    <TableCell>
                                      {formatter.format(item.total_self_price)}{" "}
                                      сум
                                    </TableCell>
                                  )}
                                  {data.status === "WRITTEN_OFF" && (
                                    <TableCell>{item.returned_count}</TableCell>
                                  )}
                                  {data.status === "CREATED" && (
                                    <TableCell className="flex items-center gap-2">
                                      <Dialog>
                                        <DialogTrigger>
                                          <Button
                                            size="icon"
                                            variant="destructive"
                                            onClick={() => setItemID(item.id)}
                                          >
                                            <Undo2 className="w-4 h-4" />
                                          </Button>
                                        </DialogTrigger>

                                        <DialogContent>
                                          <DialogHeader>
                                            <DialogTitle>
                                              Списание товара
                                            </DialogTitle>
                                          </DialogHeader>

                                          <AddForm
                                            form={writeOffForm}
                                            onSubmit={writeOffSubmit}
                                            success={writeOffSuccess}
                                            successDesc="Ингридиент успешно списан"
                                          >
                                            {writeOffError && (
                                              <ErrorItem
                                                title="Ошибка"
                                                desc={writeOffErrorText}
                                              />
                                            )}

                                            <NumberFormField
                                              _value={writeOffNumberValue}
                                              _onChange={
                                                handleWriteOffNumberChange
                                              }
                                              control={writeOffForm.control}
                                              name="write_off_count"
                                              label="Количество товара"
                                              placeholder="Введите количество товара"
                                            />

                                            <Button
                                              type="submit"
                                              disabled={writeOffPending}
                                            >
                                              Списать товар
                                            </Button>
                                          </AddForm>
                                        </DialogContent>
                                      </Dialog>

                                      <Button
                                        variant="destructive"
                                        size="icon"
                                        disabled={isDeleting}
                                        onClick={() =>
                                          deleteItem(
                                            `api/factories/product-factories/${id}/items`,
                                            item.id,
                                            [
                                              "Bouquets",
                                              "Factories",
                                              "Products",
                                            ]
                                          )
                                        }
                                      >
                                        <Trash2 className="w-4 h-4" />
                                      </Button>
                                    </TableCell>
                                  )}
                                  {data.status === "WRITTEN_OFF" && (
                                    <TableCell className="flex items-center gap-2">
                                      <ReturnDialog
                                        dialogTitle="Сделать возврат"
                                        dialogDesc="Заполните нужные поля, чтобы сделать возврат"
                                        schemaObject={{
                                          count: z.string({
                                            required_error:
                                              "Введите количество товара",
                                          }),
                                        }}
                                        url={`api/factories/product-factories/${id}/items/${item.id}/returns/`}
                                        invalidatesTags={[
                                          "Bouquets",
                                          "Factories",
                                          "Products",
                                          "OrderReturns",
                                        ]}
                                      />

                                      <Dialog>
                                        <DialogTrigger asChild>
                                          <Button
                                            size="icon"
                                            onClick={() =>
                                              setFactoryItemID(item.id)
                                            }
                                          >
                                            <Eye className="w-4 h-4" />
                                          </Button>
                                        </DialogTrigger>

                                        <DialogContent className="w-full">
                                          <DialogHeader>
                                            <DialogTitle>
                                              Возвращенные товары
                                            </DialogTitle>
                                          </DialogHeader>

                                          {error && (
                                            <ErrorItem
                                              title="Ошибка"
                                              desc="Error"
                                            />
                                          )}

                                          <Table className="w-full">
                                            <TableHeader>
                                              <TableRow>
                                                <TableHead>№</TableHead>
                                                <TableHead>
                                                  Количество
                                                </TableHead>
                                                <TableHead>Итого</TableHead>
                                                {userType !==
                                                  "WAREHOUSE_MASTER" && (
                                                  <TableHead>
                                                    Себестоимость
                                                  </TableHead>
                                                )}
                                                <TableHead>
                                                  Дата возврата
                                                </TableHead>
                                              </TableRow>
                                            </TableHeader>

                                            <TableBody>
                                              {factoryItemsReturns &&
                                                Array.isArray(
                                                  factoryItemsReturns
                                                ) &&
                                                factoryItemsReturns.map(
                                                  (item, index) => (
                                                    <TableRow key={item.id}>
                                                      <TableCell>
                                                        {++index}
                                                      </TableCell>
                                                      <TableCell>
                                                        {formatter.format(
                                                          item.count
                                                        )}
                                                      </TableCell>
                                                      <TableCell>
                                                        {formatter.format(
                                                          item.total_price
                                                        )}{" "}
                                                        сум
                                                      </TableCell>
                                                      {userType !==
                                                        "WAREHOUSE_MASTER" && (
                                                        <TableCell>
                                                          {formatter.format(
                                                            item.total_self_price
                                                          )}{" "}
                                                          сум
                                                        </TableCell>
                                                      )}
                                                      <TableCell>
                                                        {formatDate(
                                                          item.created_at
                                                        )}
                                                      </TableCell>
                                                      <TableCell>
                                                        <Button
                                                          variant="destructive"
                                                          size="icon"
                                                          disabled={isDeleting}
                                                          onClick={() =>
                                                            deleteItem(
                                                              `api/factories/product-factories/${id}/items/${factoryItemID}/returns`,
                                                              item.id,
                                                              [
                                                                "Bouquets",
                                                                "Factories",
                                                                "Products",
                                                                "OrderReturns",
                                                              ]
                                                            )
                                                          }
                                                        >
                                                          <Trash2 className="w-4 h-4" />
                                                        </Button>
                                                      </TableCell>
                                                    </TableRow>
                                                  )
                                                )}
                                            </TableBody>

                                            {factoryItemsReturns &&
                                              Array.isArray(
                                                factoryItemsReturns
                                              ) &&
                                              factoryItemsReturns.length ===
                                                0 && (
                                                <p className="w-full mt-2 p-2 text-lg font-medium">
                                                  Возвращённых ингридиентов нет
                                                </p>
                                              )}
                                          </Table>
                                        </DialogContent>
                                      </Dialog>
                                    </TableCell>
                                  )}
                                </TableRow>
                              ))}
                          </TableBody>

                          {data &&
                            data.items &&
                            Array.isArray(data.items) &&
                            data.items.length === 0 && (
                              <p className="mt-4 text-xl font-bold">
                                Добавьте материалы
                              </p>
                            )}
                        </Table>
                      ) : (
                        <SectionTableSkeleton />
                      )}
                    </ScrollArea>
                  </div>
                </div>

                <div
                  className={`${
                    userType !== "ADMIN" &&
                    userType !== "MANAGER" &&
                    userType !== "WAREHOUSE_MASTER" &&
                    userType !== "CRAFTER"
                      ? "opacity-60 pointer-events-none select-none"
                      : ""
                  } w-full mt-4 pb-2 flex flex-col sm:flex-row justify-between gap-4 bg-transparent`}
                >
                  <div className="flex flex-col items-start gap-1">
                    <p>
                      Себестоимость:{" "}
                      <span className="font-semibold">
                        {formatter.format(data.self_price)} сум
                      </span>
                    </p>
                    <p>
                      Цена продажи:{" "}
                      <span className="font-semibold">
                        {formatter.format(data.price)} сум
                      </span>
                    </p>
                  </div>

                  {data.items &&
                  Array.isArray(data.items) &&
                  data.items.length !== 0 ? (
                    <div className="flex items-center justify-end gap-2">
                      {data.status === "FINISHED" && (
                        <a
                          href={`${getUrl()}/core/print-receipt/factory/${
                            data.id
                          }/`}
                          target="_blank"
                        >
                          <Button>
                            <ScanLine className="mr-2 w-4 h-4" /> Распечатать
                            штрих код
                          </Button>
                        </a>
                      )}
                      {data.status === "CREATED" && (
                        <Button
                          onClick={() => changeStatus("finish")}
                          disabled={statusPending}
                        >
                          Собрать букет
                        </Button>
                      )}
                      {data.status === "FINISHED" && (
                        <Button
                          variant="destructive"
                          onClick={() =>
                            changeStatus("request_return_to_create")
                          }
                          disabled={statusPending}
                        >
                          Разобрать букет
                        </Button>
                      )}
                      {data.status !== "WRITTEN_OFF" &&
                        data.status !== "SOLD" &&
                        data.status !== "PENDING" && (
                          <Dialog>
                            <DialogTrigger>
                              <Button variant="destructive">
                                Списать букет
                              </Button>
                            </DialogTrigger>

                            <DialogContent>
                              <DialogHeader>
                                <DialogTitle>
                                  Вы действительно хотите списать букет?
                                </DialogTitle>
                              </DialogHeader>

                              <div className="flex items-center gap-2">
                                <Button
                                  variant="destructive"
                                  disabled={statusPending}
                                  onClick={() =>
                                    changeStatus("request_write_off")
                                  }
                                >
                                  Да
                                </Button>
                                <DialogTrigger>
                                  <Button>Нет</Button>
                                </DialogTrigger>
                              </div>
                            </DialogContent>
                          </Dialog>
                        )}
                    </div>
                  ) : null}
                </div>
              </section>
            </div>
          </>
        ) : (
          <EditSectionSkeleton />
        )}
      </DashboardLayout>
    </>
  );
};

export default BouquetsEditPage;

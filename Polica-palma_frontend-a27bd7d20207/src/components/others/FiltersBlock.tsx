/* eslint-disable @typescript-eslint/no-explicit-any */
import DatePicker from "@/components/others/DatePicker.tsx";
import SelectBlock from "@/components/others/SelectBlock.tsx";
import { SelectItem } from "@/components/ui/select.tsx";
import SelectItemSkeleton from "@/components/skeletons/SelectItemSkeleton.tsx";
import { Button } from "@/components/ui/button.tsx";
import MultiSelect from "@/components/others/MultiSelect.tsx";
import TimeDatePicker from "@/components/others/TimeDatePicker.tsx";
import React from "react";
import { api } from "@/services/api.ts";
import clsx from "clsx";
import { useLocation } from "react-router-dom";

interface FiltersBlockProps {
  periodFrom?: any;
  periodTo?: any;
  setPeriodFrom?: any;
  setPeriodTo?: any;
  periodFromTime?: any;
  periodToTime?: any;
  setPeriodFromTime?: any;
  setPeriodToTime?: any;
  fromTime?: any;
  toTime?: any;
  setFromTime?: any;
  setToTime?: any;
  refetchData?: (() => void) | undefined;
  pathName?: any;

  generateText?: string;
  statusApiUrl?: string;
  indicatorApiUrl?: string;
  createdApiUrl?: string;

  status?: any;
  provider?: any;
  industry?: any;
  productsCategory?: any;
  factoriesCategory?: any;
  client?: any;
  createdUserValue?: any;
  hasDebtValue?: any;
  salesmanValue?: any;
  paymentType?: any;
  paymentModelType?: any;
  paymentMethod?: any;
  outlay?: any;
  created?: any;
  worker?: any;
  isDebt?: any;
  outlayType?: any;
  salesType?: any;
  florist?: any;
  indicatorValue?: any;
  incomeType?: any;
  incomeReason?: any;
  workerType?: any;
  orderField?: any;

  setIndustry?: (e: any) => void;
  setProductsCategory?: (e: any) => void;
  setFactoriesCategory?: (e: any) => void;
  setClients?: (e: any) => void;
  setStatus?: (e: any) => void;
  setPaymentType?: (e: any) => void;
  setPaymentModelType?: (e: any) => void;
  setPaymentMethod?: (e: any) => void;
  setOutlayType?: (e: any) => void;
  setFlorist?: (e: any) => void;
  setCreatedUser?: (e: any) => void;
  setSalesType?: (e: any) => void;
  setHasDebt?: (e: any) => void;
  setOutlay?: (e: any) => void;
  setIndicator?: (e: any) => void;
  setSalesman?: (e: any) => void;
  setCreated?: (e: any) => void;
  setProvider?: (e: any) => void;
  setWorker?: (e: any) => void;
  setIncomeType?: (e: any) => void;
  setIncomeReason?: (e: any) => void;
  setIsDebt?: (e: any) => void;
  setWorkerType?: (e: any) => void;
  setOrderField?: (e: any) => void;

  hasProductsCategory?: boolean;
  hasFactoriesCategory?: boolean;
  hasIndustry?: boolean;
  hasStatus?: boolean;
  hasClients?: boolean;
  haventPeriods?: boolean;
  hasPaymentMethod?: boolean;
  hasPaymentType?: boolean;
  hasPaymentModelType?: boolean;
  hasOutlayType?: boolean;
  hasFlorist?: boolean;
  hasCreatedUser?: boolean;
  hasSalesType?: boolean;
  hasDebt?: boolean;
  hasOutlay?: boolean;
  hasIndicator?: boolean;
  hasSalesman?: boolean;
  hasCreated?: boolean;
  hasProvider?: boolean;
  hasWorker?: boolean;
  hasTimePeriods?: boolean;
  hasIncomeType?: boolean;
  hasIncomeReason?: boolean;
  hasIsDebt?: boolean;
  hasWorkerType?: boolean;
  hasOrderField?: boolean;

  industryNotMulti?: boolean;
  statusNotMulti?: boolean;
  productsCategoryNotMulti?: boolean;
  factoriesCategoryNotMulti?: boolean;
  clientsNotMulti?: boolean;
  paymentMethodNotMulti?: boolean;
  paymentTypeNotMulti?: boolean;
  paymentModelTypeNotMulti?: boolean;
  outlayTypeNotMulti?: boolean;
  floristNotMulti?: boolean;

  hasntBtns?: boolean;
}

const FiltersBlock = ({
  fromTime,
  setFromTime,
  toTime,
  setToTime,
  hasTimePeriods,
  periodFromTime,
  periodToTime,
  setPeriodToTime,
  setPeriodFromTime,
  periodFrom,
  periodTo,
  setPeriodFrom,
  setPeriodTo,
  setIndustry,
  setProductsCategory,
  setFactoriesCategory,
  setStatus,
  refetchData,
  hasProductsCategory,
  hasFactoriesCategory,
  hasIndustry,
  hasStatus,
  statusApiUrl = "",
  haventPeriods,
  hasClients,
  setClients,
  setPaymentType,
  setPaymentMethod,
  setPaymentModelType,
  hasPaymentType,
  hasPaymentMethod,
  hasPaymentModelType,
  setOutlayType,
  hasOutlayType,
  hasFlorist,
  setFlorist,
  statusNotMulti,
  industryNotMulti,
  productsCategoryNotMulti,
  factoriesCategoryNotMulti,
  clientsNotMulti,
  paymentMethodNotMulti,
  paymentTypeNotMulti,
  paymentModelTypeNotMulti,
  outlayTypeNotMulti,
  floristNotMulti,
  hasCreatedUser,
  setCreatedUser,
  hasSalesType,
  setSalesType,
  setHasDebt,
  hasDebt,
  setOutlay,
  hasOutlay,
  hasntBtns,
  hasIndicator,
  setIndicator,
  indicatorApiUrl = "",
  setSalesman,
  hasSalesman,
  createdApiUrl = "",
  hasCreated,
  setCreated,
  hasProvider,
  setProvider,
  hasWorker,
  setWorker,
  setIncomeType,
  hasIncomeType,
  hasIncomeReason,
  setIncomeReason,
  hasIsDebt,
  setIsDebt,
  pathName,
  status,
  provider,
  industry,
  productsCategory,
  factoriesCategory,
  client,
  createdUserValue,
  hasDebtValue,
  salesmanValue,
  paymentType,
  paymentModelType,
  paymentMethod,
  outlay,
  created,
  worker,
  isDebt,
  outlayType,
  salesType,
  florist,
  indicatorValue,
  incomeType,
  incomeReason,
  hasWorkerType,
  setWorkerType,
  workerType,
  generateText,
  hasOrderField,
  orderField,
  setOrderField,
}: FiltersBlockProps) => {
  const debtData = [
    { label: "Да", value: "true" },
    { label: "Нет", value: "false" },
  ];

  const orderFieldsData = [
    { label: "Общая сумма заказов", value: "total_orders_sum" },
    { label: "Количество заказов", value: "orders_count" },
    { label: "Сумма долга", value: "debt" },
  ];

  const { data: industriesData, isLoading: industriesLoading } =
    api.useGetIndustriesQuery("");
  const { data: providersData, isLoading: providersLoading } =
    api.useGetProvidersQuery("");
  const { data: productsCategoriesData, isLoading: productsCategoriesLoading } =
    api.useGetCategoriesQuery("");
  const {
    data: factoriesCategoriesData,
    isLoading: factoriesCategoriesLoading,
  } = api.useGetFactoriesCategoriesQuery("");
  const { data: clientsData, isLoading: clientsLoading } =
    api.useGetClientsQuery("");
  const { data: paymentMethodsData, isLoading: paymentMethodsLoading } =
    api.useGetPaymentMethodsQuery("");
  const { data: createOptionsData, isLoading: createOptionsLoading } =
    api.useGetPaymentCreateOptionsQuery("");
  const { data: filterOptionsData, isLoading: filterOptionsLoading } =
    api.useGetPaymentFilterOptionsQuery("");
  const { data: outlayTypesData, isLoading: outlayTypesLoading } =
    api.useGetOutlaysTypesQuery("");
  const { data: floristData, isLoading: floristLoading } =
    api.useGetFloristsQuery("");
  const { data: createdUserData, isLoading: createdUserLoading } =
    api.useGetHaveOrdersUsersQuery("");
  const { data: salesTypesData, isLoading: salesTypesLoading } =
    api.useGetFactoriesSalesTypesQuery("");
  const { data: outlayData, isLoading: outlayLoading } =
    api.useGetOutlaysQuery("");
  const { data: salesmanData, isLoading: salesmanLoading } =
    api.useGetSalesmanQuery("");
  const { data: workersData, isLoading: workersLoading } =
    api.useGetWorkersQuery("");
  const { data: incomeTypesData, isLoading: incomeTypesLoading } =
    api.useGetWorkerIncomeTypesQuery("");
  const { data: incomeReasons, isLoading: incomeReasonsLoading } =
    api.useGetIncomeReasonsQuery("");
  const { data: workerTypes, isLoading: workerTypesLoading } =
    api.useGetAllWorkersReportTypeOptionsQuery("");
  const { data: indicatorData, isLoading: indicatorLoading } =
    api.useGetIndicatorQuery(indicatorApiUrl);
  const { data: statusesData, isLoading: statusesLoading } =
    api.useGetStatusesQuery(statusApiUrl);
  const { data: createdData, isLoading: createdLoading } =
    api.useGetCreatedQuery(createdApiUrl);

  const extractValue = (selectedOption: any, returnType: "value" | "id") => {
    const getValueOrId = (option: any) => {
      if (returnType === "value") {
        return option.value;
      } else if (returnType === "id") {
        return option.id?.toString();
      }

      return null;
    };

    if (Array.isArray(selectedOption)) {
      return selectedOption.map(getValueOrId);
    }

    return selectedOption ? getValueOrId(selectedOption) : null;
  };

  const handleFromTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFromTime(e.target.value);
    setPeriodFromTime((prevDate: any) =>
      prevDate
        ? new Date(prevDate.setHours(...e.target.value.split(":")))
        : prevDate
    );
  };

  const handleToTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setToTime(e.target.value);
    setPeriodFromTime((prevDate: any) =>
      prevDate
        ? new Date(prevDate.setHours(...e.target.value.split(":")))
        : prevDate
    );
  };

  const handleMultiSelectChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setClients ? setClients(extractValue(e, "id")) : null;
  };

  //Clear Filter
  const clearFilters = () => {
    // setClients ? setClients([]) : null;
    localStorage.removeItem(pathName);
    // setOrderField ? setOrderField([]) : null;
    // setPeriodFrom(null);
    // setPeriodTo(null);

    //Временно )
    location.reload();
  };

  const locations = useLocation();


  return (
    <>
      <div className={clsx("w-full flex items-center gap-3 relative", locations.pathname == "/" && "mb-[50px]")}>
        {!haventPeriods && (
          <>
            <DatePicker
              date={periodFrom}
              setDate={setPeriodFrom}
              text="Дата начала"
            />
            <DatePicker
              date={periodTo}
              setDate={setPeriodTo}
              text="Дата конца"
            />
          </>
        )}

        {hasTimePeriods && (
          <>
            <TimeDatePicker
              time={fromTime}
              date={periodFromTime}
              setDate={setPeriodFromTime}
              handleTimeChange={handleFromTimeChange}
              text="Дата начала"
            />
            <TimeDatePicker
              time={toTime}
              date={periodToTime}
              setDate={setPeriodToTime}
              handleTimeChange={handleToTimeChange}
              text="Дата конца"
            />
          </>
        )}

        {hasIndustry && (
          <>
            {industryNotMulti ? (
              <SelectBlock
                placeholder="Магазин"
                onValueChange={(e: any) =>
                  setIndustry ? setIndustry(e) : null
                }
              >
                <SelectItem value="null">Не выбрано</SelectItem>

                {!industriesLoading &&
                industriesData &&
                Array.isArray(industriesData) ? (
                  industriesData.map((item) => (
                    <SelectItem key={item.id} value={item.id.toString()}>
                      {item.name}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItemSkeleton />
                )}
              </SelectBlock>
            ) : (
              <MultiSelect
                isID
                idOptions={industriesData}
                onChange={(e: any) =>
                  setIndustry ? setIndustry(extractValue(e, "id")) : null
                }
                placeholder="Магазин"
                isLoading={industriesLoading}
                defaultValues={industry}
              />
            )}
          </>
        )}

        {hasProvider && (
          <MultiSelect
            isID
            idOptions={providersData}
            onChange={(e: any) =>
              setProvider ? setProvider(extractValue(e, "id")) : null
            }
            placeholder="Поставщик"
            isLoading={providersLoading}
            defaultValues={provider}
          />
        )}

        {hasProductsCategory && (
          <>
            {productsCategoryNotMulti ? (
              <SelectBlock
                placeholder="Категория товаров"
                onValueChange={(e: any) =>
                  setProductsCategory ? setProductsCategory(e) : null
                }
              >
                <SelectItem value="null">Не выбрано</SelectItem>

                {!productsCategoriesLoading &&
                productsCategoriesData &&
                Array.isArray(productsCategoriesData) ? (
                  productsCategoriesData.map((item) => (
                    <SelectItem key={item.id} value={item.id.toString()}>
                      {item.name}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItemSkeleton />
                )}
              </SelectBlock>
            ) : (
              <MultiSelect
                isID
                idOptions={productsCategoriesData}
                onChange={(e: any) =>
                  setProductsCategory
                    ? setProductsCategory(extractValue(e, "id"))
                    : null
                }
                placeholder="Категория товаров"
                isLoading={productsCategoriesLoading}
                defaultValues={productsCategory}
              />
            )}
          </>
        )}

        {hasFactoriesCategory && (
          <>
            {factoriesCategoryNotMulti ? (
              <SelectBlock
                placeholder="Категория букетов"
                onValueChange={(e: any) =>
                  setFactoriesCategory ? setFactoriesCategory(e) : null
                }
              >
                <SelectItem value="null">Не выбрано</SelectItem>

                {!factoriesCategoriesLoading &&
                factoriesCategoriesData &&
                Array.isArray(factoriesCategoriesData) ? (
                  factoriesCategoriesData.map((item) => (
                    <SelectItem key={item.id} value={item.id.toString()}>
                      {item.name}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItemSkeleton />
                )}
              </SelectBlock>
            ) : (
              <MultiSelect
                isID
                idOptions={factoriesCategoriesData}
                onChange={(e: any) =>
                  setFactoriesCategory
                    ? setFactoriesCategory(extractValue(e, "id"))
                    : null
                }
                placeholder="Категория букетов"
                isLoading={factoriesCategoriesLoading}
                defaultValues={factoriesCategory}
              />
            )}
          </>
        )}

        {hasStatus && (
          <>
            {statusNotMulti ? (
              <SelectBlock
                placeholder="Статус"
                onValueChange={(e: any) => (setStatus ? setStatus(e) : null)}
              >
                <SelectItem value="null">Не выбрано</SelectItem>

                {!statusesLoading &&
                statusesData &&
                Array.isArray(statusesData) ? (
                  statusesData.map((item, index) => (
                    <SelectItem key={index} value={item.value}>
                      {item.label}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItemSkeleton />
                )}
              </SelectBlock>
            ) : (
              <MultiSelect
                valueOptions={statusesData}
                onChange={(e: any) =>
                  setStatus ? setStatus(extractValue(e, "value")) : null
                }
                placeholder="Статус"
                isLoading={statusesLoading}
                defaultValues={status}
              />
            )}
          </>
        )}

        {hasClients && (
          <>
            {clientsNotMulti ? (
              <SelectBlock
                placeholder="Клиент"
                onValueChange={(e: any) => (setClients ? setClients(e) : null)}
              >
                <SelectItem value="null">Не выбрано</SelectItem>

                {!clientsLoading &&
                clientsData &&
                Array.isArray(clientsData) ? (
                  clientsData.map((item) => (
                    <SelectItem key={item.id} value={item.id.toString()}>
                      {item.full_name}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItemSkeleton />
                )}
              </SelectBlock>
            ) : (
              <MultiSelect
                isLianerDiagramSelectFilter
                isID
                idOptions={clientsData}
                onChange={(e: any) => handleMultiSelectChange(e)}
                placeholder="Клиент"
                isLoading={clientsLoading}
                defaultValues={client}
              />
            )}
          </>
        )}

        {hasSalesman && (
          <MultiSelect
            isID
            idOptions={salesmanData}
            onChange={(e: any) =>
              setSalesman ? setSalesman(extractValue(e, "id")) : null
            }
            placeholder="Продавец"
            isLoading={salesmanLoading}
            defaultValues={salesmanValue}
          />
        )}

        {hasPaymentMethod && (
          <>
            {paymentMethodNotMulti ? (
              <SelectBlock
                placeholder="Метод оплаты"
                onValueChange={(e: any) =>
                  setPaymentMethod ? setPaymentMethod(e) : null
                }
              >
                <SelectItem value="null">Не выбрано</SelectItem>

                {!paymentMethodsLoading &&
                paymentMethodsData &&
                Array.isArray(paymentMethodsData) ? (
                  paymentMethodsData.map((item) => (
                    <SelectItem key={item.id} value={item.id.toString()}>
                      {item.name}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItemSkeleton />
                )}
              </SelectBlock>
            ) : (
              <MultiSelect
                isID
                idOptions={paymentMethodsData}
                onChange={(e: any) =>
                  setPaymentMethod
                    ? setPaymentMethod(extractValue(e, "id"))
                    : null
                }
                placeholder="Метод оплаты"
                isLoading={paymentMethodsLoading}
                defaultValues={paymentMethod}
              />
            )}
          </>
        )}

        {hasPaymentType && (
          <>
            {paymentTypeNotMulti ? (
              <SelectBlock
                placeholder="Доход или расход"
                onValueChange={(e: any) =>
                  setPaymentType ? setPaymentType(e) : null
                }
              >
                <SelectItem value="null">Не выбрано</SelectItem>

                {!createOptionsLoading &&
                createOptionsData.payment_types &&
                Array.isArray(createOptionsData.payment_types) ? (
                  createOptionsData.payment_types.map(
                    (item: any, index: any) => (
                      <SelectItem key={index} value={item.value}>
                        {item.label}
                      </SelectItem>
                    )
                  )
                ) : (
                  <SelectItemSkeleton />
                )}
              </SelectBlock>
            ) : (
              <MultiSelect
                valueOptions={createOptionsData?.payment_types}
                onChange={(e: any) =>
                  setPaymentType
                    ? setPaymentType(extractValue(e, "value"))
                    : null
                }
                placeholder="Доход или расход"
                isLoading={createOptionsLoading}
                defaultValues={paymentType}
              />
            )}
          </>
        )}

        {hasPaymentModelType && (
          <>
            {paymentModelTypeNotMulti ? (
              <SelectBlock
                placeholder="Тип оплаты"
                onValueChange={(e: any) =>
                  setPaymentModelType ? setPaymentModelType(e) : null
                }
              >
                <SelectItem value="null">Не выбрано</SelectItem>

                {!filterOptionsLoading &&
                filterOptionsData.payment_model_types &&
                Array.isArray(filterOptionsData.payment_model_types) ? (
                  filterOptionsData.payment_model_types.map(
                    (item: any, index: any) => (
                      <SelectItem key={index} value={item.value}>
                        {item.label}
                      </SelectItem>
                    )
                  )
                ) : (
                  <SelectItemSkeleton />
                )}
              </SelectBlock>
            ) : (
              <MultiSelect
                valueOptions={filterOptionsData?.payment_model_types}
                onChange={(e: any) =>
                  setPaymentModelType
                    ? setPaymentModelType(extractValue(e, "value"))
                    : null
                }
                placeholder="Тип оплаты"
                isLoading={filterOptionsLoading}
                defaultValues={paymentModelType}
              />
            )}
          </>
        )}

        {hasOutlayType && (
          <>
            {outlayTypeNotMulti ? (
              <SelectBlock
                placeholder="Тип расхода"
                onValueChange={(e: any) =>
                  setOutlayType ? setOutlayType(e) : null
                }
              >
                <SelectItem value="null">Не выбрано</SelectItem>

                {!outlayTypesLoading &&
                outlayTypesData &&
                Array.isArray(outlayTypesData) ? (
                  outlayTypesData.map((item, index) => (
                    <SelectItem key={index} value={item.value}>
                      {item.label}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItemSkeleton />
                )}
              </SelectBlock>
            ) : (
              <MultiSelect
                valueOptions={outlayTypesData}
                onChange={(e: any) =>
                  setOutlayType ? setOutlayType(extractValue(e, "value")) : null
                }
                placeholder="Тип расхода"
                isLoading={outlayTypesLoading}
                defaultValues={outlayType}
              />
            )}
          </>
        )}

        {hasIncomeType && (
          <MultiSelect
            valueOptions={incomeTypesData}
            onChange={(e: any) =>
              setIncomeType ? setIncomeType(extractValue(e, "value")) : null
            }
            placeholder="Тип начисления"
            isLoading={incomeTypesLoading}
            defaultValues={incomeType}
          />
        )}

        {hasFlorist && (
          <>
            {floristNotMulti ? (
              <SelectBlock
                placeholder="Флорист"
                onValueChange={(e: any) => (setFlorist ? setFlorist(e) : null)}
              >
                <SelectItem value="null">Не выбрано</SelectItem>

                {!floristLoading &&
                floristData &&
                Array.isArray(floristData) ? (
                  floristData.map((item) => (
                    <SelectItem key={item.id} value={item.id.toString()}>
                      {item.first_name || item.username}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItemSkeleton />
                )}
              </SelectBlock>
            ) : (
              <MultiSelect
                isID
                idOptions={floristData}
                onChange={(e: any) =>
                  setFlorist ? setFlorist(extractValue(e, "id")) : null
                }
                placeholder="Флорист"
                isLoading={floristLoading}
                defaultValues={florist}
              />
            )}
          </>
        )}

        {hasCreatedUser && (
          <MultiSelect
            isID
            idOptions={createdUserData}
            onChange={(e: any) =>
              setCreatedUser ? setCreatedUser(extractValue(e, "id")) : null
            }
            placeholder="Создатель"
            isLoading={createdUserLoading}
            defaultValues={createdUserValue}
          />
        )}

        {hasCreated && (
          <MultiSelect
            isID
            idOptions={createdData}
            onChange={(e: any) =>
              setCreated ? setCreated(extractValue(e, "id")) : null
            }
            placeholder="Создатель"
            isLoading={createdLoading}
            defaultValues={created}
          />
        )}

        {hasSalesType && (
          <MultiSelect
            valueOptions={salesTypesData}
            onChange={(e: any) =>
              setSalesType ? setSalesType(extractValue(e, "value")) : null
            }
            placeholder="Тип продажи"
            isLoading={salesTypesLoading}
            defaultValues={salesType}
          />
        )}

        {hasDebt && (
          <MultiSelect
            valueOptions={debtData}
            onChange={(e: any) =>
              setHasDebt ? setHasDebt(extractValue(e, "value")) : null
            }
            placeholder="Есть долг"
            defaultValues={hasDebtValue}
          />
        )}

        {hasOutlay && (
          <MultiSelect
            isID
            idOptions={outlayData}
            onChange={(e: any) =>
              setOutlay ? setOutlay(extractValue(e, "id")) : null
            }
            placeholder="Причина расхода"
            isLoading={outlayLoading}
            defaultValues={outlay}
          />
        )}

        {hasWorker && (
          <MultiSelect
            isID
            idOptions={workersData}
            onChange={(e: any) =>
              setWorker ? setWorker(extractValue(e, "id")) : null
            }
            placeholder="Сотрудник"
            isLoading={workersLoading}
            defaultValues={worker}
          />
        )}

        {hasIncomeReason && (
          <MultiSelect
            valueOptions={incomeReasons}
            onChange={(e: any) =>
              setIncomeReason ? setIncomeReason(extractValue(e, "value")) : null
            }
            placeholder="Причина начисления"
            isLoading={incomeReasonsLoading}
            defaultValues={incomeReason}
          />
        )}

        {hasIsDebt && (
          <SelectBlock
            placeholder="Оплата долга"
            onValueChange={(e: any) => (setIsDebt ? setIsDebt(e) : null)}
            defaultValue={isDebt}
          >
            <SelectItem value="null">Не выбрано</SelectItem>

            {debtData && Array.isArray(debtData) ? (
              debtData.map((item, index) => (
                <SelectItem key={index} value={item.value}>
                  {item.label}
                </SelectItem>
              ))
            ) : (
              <SelectItemSkeleton />
            )}
          </SelectBlock>
        )}

        {hasWorkerType && (
          <MultiSelect
            valueOptions={workerTypes}
            onChange={(e: any) =>
              setWorkerType ? setWorkerType(extractValue(e, "value")) : null
            }
            placeholder="Тип сотрудника"
            isLoading={workerTypesLoading}
            defaultValues={workerType}
          />
        )}

        {hasIndicator && (
          <SelectBlock
            placeholder="Индикатор"
            onValueChange={(e: any) => (setIndicator ? setIndicator(e) : null)}
            defaultValue={indicatorValue}
          >
            <SelectItem value="null">Не выбрано</SelectItem>

            {!indicatorLoading &&
            indicatorData &&
            Array.isArray(indicatorData) ? (
              indicatorData.map((item, index) => (
                <SelectItem key={index} value={item.value}>
                  {item.label}
                </SelectItem>
              ))
            ) : (
              <SelectItemSkeleton />
            )}
          </SelectBlock>
        )}

        {hasOrderField && (
          <SelectBlock
            placeholder="Значение"
            onValueChange={(e: any) =>
              setOrderField ? setOrderField(e) : null
            }
            defaultValue={orderField}
          >
            <SelectItem value="null">Не выбрано</SelectItem>

            {orderFieldsData.map((item: any, index: any) => (
              <SelectItem key={index} value={item.value}>
                {item.label}
              </SelectItem>
            ))}
          </SelectBlock>
        )}

        {!hasntBtns && (
          <div className="flex items-center gap-2">
            <Button onClick={refetchData}>
              {generateText ? generateText : "Применить"}
            </Button>
            <Button variant="destructive" onClick={clearFilters}>
              Сбросить
            </Button>
          </div>
        )}
      </div>
    </>
  );
};

export default FiltersBlock;

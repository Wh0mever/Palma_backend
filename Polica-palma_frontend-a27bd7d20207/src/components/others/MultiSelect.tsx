import Select from "react-select";
import makeAnimated from "react-select/animated";

import { useLocation } from "react-router-dom";
const animatedComponents = makeAnimated();

interface MultiSelectProps {
  isID?: boolean;
  idOptions?: any;
  valueOptions?: any;
  defaultValues?: any;
  onChange: (e: any) => void;
  placeholder?: string | undefined;
  isLoading?: boolean;
  isLianerDiagramSelectFilter?: boolean;
}

const MultiSelect = ({
  isID,
  idOptions,
  valueOptions,
  onChange,
  placeholder,
  isLoading,
  defaultValues,
  isLianerDiagramSelectFilter,
}: MultiSelectProps) => {
  let _defaultValues = [];

  if (isID && idOptions !== undefined) {
    _defaultValues = idOptions.filter((v: any) => {
      return defaultValues?.indexOf(String(v.id)) >= 0;
    });
  } else if (valueOptions !== undefined)
    _defaultValues = valueOptions.filter((v: any) => {
      return defaultValues?.indexOf(String(v.value)) >= 0;
    });

  const location = useLocation();

  return (
    <>
      {location?.pathname == "/" && isLianerDiagramSelectFilter ? (
        <div className="absolute left-0 right-0 bottom-[-50px]">
          <Select
            className="z-40 w-full text-sm rounded-md"
            components={animatedComponents}
            options={isID ? idOptions : valueOptions}
            value={isID ? idOptions?.id : valueOptions?.value}
            defaultValue={_defaultValues}
            onChange={onChange}
            placeholder={placeholder}
            isClearable
            isSearchable
            isMulti
            isOptionDisabled={() => _defaultValues?.length >= 10}
            isLoading={isLoading}
            getOptionValue={
              isID
                ? (option: any) => String(option.id)
                : (option: any) => option.value
            }
            getOptionLabel={
              isID
                ? (option: any) =>
                    option.name ||
                    option.full_name ||
                    option.first_name ||
                    option.username ||
                    option.title
                : (option: any) => option.label
            }
          />
        </div>
      ) : (
        <Select
          className="z-40 w-full text-sm rounded-md"
          components={animatedComponents}
          options={isID ? idOptions : valueOptions}
          value={isID ? idOptions?.id : valueOptions?.value}
          defaultValue={_defaultValues}
          onChange={onChange}
          placeholder={placeholder}
          isClearable
          isSearchable
          isMulti
          isOptionDisabled={() => _defaultValues?.length >= 10}
          isLoading={isLoading}
          getOptionValue={
            isID
              ? (option: any) => String(option.id)
              : (option: any) => option.value
          }
          getOptionLabel={
            isID
              ? (option: any) =>
                  option.name ||
                  option.full_name ||
                  option.first_name ||
                  option.username ||
                  option.title
              : (option: any) => option.label
          }
        />
      )}
    </>
  );
};

export default MultiSelect;

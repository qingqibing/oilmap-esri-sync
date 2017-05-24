using System.Runtime.InteropServices;
using System.Text;
using System;
public class NetCDF
{
    public enum nc_type
    {
        NC_BYTE = 1,
        NC_CHAR = 2,
        NC_SHORT = 3,
        NC_INT = 4,
        NC_FLOAT = 5,
        NC_DOUBLE = 6
    }
    public enum cmode
    {
        NC_NOWRITE = 0,
        NC_WRITE = 1,
        NC_CLOBBER = 0,
        NC_NOCLOBBER = 4,
        NC_FILL = 0,
        NC_NOFILL = 256,
        NC_LOCK = 1024,
        NC_SHARE = 2048
    }
    public const byte NC_FILL_BYTE = 255;
    public const byte NC_FILL_CHAR = 0;
    public const Int16 NC_FILL_SHORT = -32767;
    public const Int32 NC_FILL_INT = -2147483647;
    public const float NC_FILL_FLOAT = 9.96921E+36F;
    public const double NC_FILL_DOUBLE = 9.96920996838687E+36;
    public const Int32 NC_UNLIMITED = 0;
    public const Int32 NC_GLOBAL = -1;
    public enum netCDF_limits
    {
        NC_MAX_DIMS = 10,
        NC_MAX_ATTRS = 2000,
        NC_MAX_VARS = 2000,
        NC_MAX_NAME = 128,
        NC_MAX_VAR_DIMS = 10
    }
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern string nc_inq_libvers();
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern string nc_strerror(Int32 ncerr1);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_create(string path, Int32 cmode, ref Int32 ncidp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_open(string path, Int32 cmode, ref Int32 ncidp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_set_fill(Int32 ncid, Int32 fillmode, ref Int32 old_modep);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_redef(Int32 ncid);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_enddef(Int32 ncid);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_sync(Int32 ncid);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_abort(Int32 ncid);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_close(Int32 ncid);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq(Int32 ncid, ref Int32 ndimsp, ref Int32 nvarsp, ref Int32 nattsp, ref Int32 unlimdimidp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_ndims(Int32 ncid, ref Int32 ndimsp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_nvars(Int32 ncid, ref Int32 nvarsp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_natts(Int32 ncid, ref Int32 nattsp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_unlimdim(Int32 ncid, ref Int32 unlimdimidp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_def_dim(Int32 ncid, string name, Int32 len, ref Int32 idp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_dimid(Int32 ncid, string name, ref Int32 idp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_dim(Int32 ncid, Int32 dimid, StringBuilder name, ref Int32 lenp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_dimname(Int32 ncid, Int32 dimid, string name);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_dimlen(Int32 ncid, Int32 dimid, ref Int32 lenp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_rename_dim(Int32 ncid, Int32 dimid, string name);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_att(Int32 ncid, Int32 varid, string name, ref NetCDF.nc_type xtypep, ref Int32 lenp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_attid(Int32 ncid, Int32 varid, string name, ref NetCDF.nc_type xtypep, ref Int32 lenp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_atttype(Int32 ncid, Int32 varid, string name, ref NetCDF.nc_type xtypep, ref Int32 lenp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_attlen(Int32 ncid, Int32 varid, string name, ref Int32 lenp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_attname(Int32 ncid, Int32 varid, Int32 attnum, StringBuilder name);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_copy_att(Int32 ncid_in, Int32 varid_in, string name, Int32 ncid_out, Int32 varid_out);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_rename_att(Int32 ncid, Int32 varid, string name, ref string newname);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_del_att(Int32 ncid, Int32 varid, string name);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_att_text(Int32 ncid, Int32 varid, string name, Int32 len, string op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_att_text(Int32 ncid, Int32 varid, string name, StringBuilder op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_att_uchar(Int32 ncid, Int32 varid, string name, NetCDF.nc_type xtype, Int32 len, [In()] byte[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_att_uchar(Int32 ncid, Int32 varid, string name, [In(), Out()] byte[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_att_schar(Int32 ncid, Int32 varid, string name, NetCDF.nc_type xtype, Int32 len, [In()] byte[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_att_schar(Int32 ncid, Int32 varid, string name, [In(), Out()] byte[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_att_short(Int32 ncid, Int32 varid, string name, NetCDF.nc_type xtype, Int32 len, [In()] Int16[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_att_short(Int32 ncid, Int32 varid, string name, [In(), Out()] Int16[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_att_int(Int32 ncid, Int32 varid, string name, NetCDF.nc_type xtype, Int32 len, [In()] Int32[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_att_int(Int32 ncid, Int32 varid, string name, [In(), Out()] Int32[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_att_long(Int32 ncid, Int32 varid, string name, NetCDF.nc_type xtype, Int32 len, [In()] Int32[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_att_long(Int32 ncid, Int32 varid, string name, [In(), Out()] Int32[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_att_float(Int32 ncid, Int32 varid, string name, NetCDF.nc_type xtype, Int32 len, [In()] float[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_att_float(Int32 ncid, Int32 varid, string name, [In(), Out()] float[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_att_double(Int32 ncid, Int32 varid, string name, NetCDF.nc_type xtype, Int32 len, [In()] double[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_att_double(Int32 ncid, Int32 varid, string name, [In(), Out()] double[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_def_var(Int32 ncid, string name, nc_type xtype, Int32 ndims, [In()] int[] dimids, ref Int32 varid);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_var(Int32 ncid, Int32 varid, StringBuilder name, ref nc_type xtypep, ref Int32 ndimsp, [Out()] int[] dimidsp, ref Int32 nattsp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_varid(Int32 ncid, string name, ref Int32 varid);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_varname(Int32 ncid, Int32 varid, StringBuilder name);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_vartype(Int32 ncid, Int32 varid, ref nc_type xtypep);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_varndims(Int32 ncid, Int32 varid, ref Int32 ndimsp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_vardimid(Int32 ncid, Int32 varid, [Out()] int[] dimidsp, ref Int32 nattsp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_inq_varnatts(Int32 ncid, Int32 varid, ref Int32 nattsp);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_rename_var(Int32 ncid, Int32 varid, string name);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var1_text(Int32 ncid, Int32 varid, [In(), Out()] Int32[] indexp, string op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var1_text(Int32 ncid, Int32 varid, [In(), Out()] Int32[] indexp, StringBuilder ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var1_uchar(Int32 ncid, Int32 varid, [In(), Out()] Int32[] indexp, [In(), Out()] byte[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var1_uchar(Int32 ncid, Int32 varid, [In(), Out()] Int32[] indexp, [In(), Out()] byte[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var1_schar(Int32 ncid, Int32 varid, [In(), Out()] Int32[] indexp, [In(), Out()] byte[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var1_schar(Int32 ncid, Int32 varid, [In(), Out()] Int32[] indexp, [In(), Out()] byte[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var1_short(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] indexp, [In(), Out()]
 Int16[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var1_short(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] indexp, [In(), Out()]
 Int16[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var1_int(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] indexp, [In(), Out()]
 Int32[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var1_int(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] indexp, [In(), Out()]
 Int32[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var1_long(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] indexp, [In(), Out()]
 Int32[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var1_long(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] indexp, [In(), Out()]
 Int32[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var1_float(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] indexp, [In(), Out()]
 float[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var1_float(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] indexp, [In(), Out()]
 float[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var1_double(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] indexp, [In(), Out()]
 double[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var1_double(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] indexp, [In(), Out()]
 double[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vara_text(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] startp, [In(), Out()]
 Int32[] countp, string op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vara_text(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] startp, [In(), Out()]
 Int32[] countp, StringBuilder op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vara_uchar(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] startp, [In(), Out()]
 Int32[] countp, [In(), Out()]
 byte[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vara_uchar(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] startp, [In(), Out()]
 Int32[] countp, [In(), Out()]
 byte[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vara_schar(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] startp, [In(), Out()]
 Int32[] countp, [In(), Out()]
 byte[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vara_schar(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] startp, [In(), Out()]
 Int32[] countp, [In(), Out()]
 byte[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vara_short(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] startp, [In(), Out()]
 Int32[] countp, [In(), Out()]
 short[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vara_short(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] startp, [In(), Out()]
 Int32[] countp, [In(), Out()]
 short[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vara_int(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] startp, [In(), Out()]
 Int32[] countp, [In(), Out()]
 Int32[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vara_int(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] startp, [In(), Out()]
 Int32[] countp, [In(), Out()]
 Int32[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vara_long(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] startp, [In(), Out()]
 Int32[] countp, [In(), Out()]
 Int32[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vara_long(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] startp, [In(), Out()]
 Int32[] countp, [In(), Out()]
 Int32[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vara_float(Int32 ncid, Int32 varid, [In(), Out()]
 Int32[] startp, [In(), Out()]
 Int32[] countp, [In(), Out()]
 float[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vara_float(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
float[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vara_double(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
double[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vara_double(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
double[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vars_text(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, string op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vars_text(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, StringBuilder op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vars_uchar(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
byte[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vars_uchar(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
byte[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vars_schar(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
byte[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vars_schar(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
byte[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vars_short(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int16[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vars_short(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int16[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vars_int(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vars_int(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vars_long(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vars_long(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vars_float(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
float[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vars_float(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
float[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_vars_double(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
double[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_vars_double(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
double[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_varm_text(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, string op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_varm_text(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, StringBuilder op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_varm_uchar(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
byte[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_varm_uchar(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
byte[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_varm_schar(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
byte[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_varm_schar(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
byte[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_varm_short(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
Int16[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_varm_short(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
Int16[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_varm_int(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
Int32[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_varm_int(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
Int32[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_varm_long(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
Int32[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_varm_long(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
Int32[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_varm_float(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
float[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_varm_float(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
float[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_varm_double(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
double[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_varm_double(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] startp, [In(), Out()]
Int32[] countp, [In(), Out()]
Int32[] stridep, [In(), Out()]
Int32[] imapp, [In(), Out()]
double[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var_text(Int32 ncid, Int32 varid, string op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var_text(Int32 ncid, Int32 varid, StringBuilder ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var_uchar(Int32 ncid, Int32 varid, [In(), Out()]
byte[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var_uchar(Int32 ncid, Int32 varid, [In(), Out()]
byte[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var_schar(Int32 ncid, Int32 varid, [In(), Out()]
byte[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var_schar(Int32 ncid, Int32 varid, [In(), Out()]
byte[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var_short(Int32 ncid, Int32 varid, [In(), Out()]
Int16[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var_short(Int32 ncid, Int32 varid, [In(), Out()]
Int16[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var_int(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var_int(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var_long(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var_long(Int32 ncid, Int32 varid, [In(), Out()]
Int32[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var_float(Int32 ncid, Int32 varid, [In(), Out()]
float[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var_float(Int32 ncid, Int32 varid, [In(), Out()]
float[] ip);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_put_var_double(Int32 ncid, Int32 varid, [In(), Out()]
double[] op);
    [DllImport("netcdf.dll", CharSet = CharSet.Ansi)]
    public static extern Int32 nc_get_var_double(Int32 ncid, Int32 varid, [In(), Out()]
double[] ip);
}
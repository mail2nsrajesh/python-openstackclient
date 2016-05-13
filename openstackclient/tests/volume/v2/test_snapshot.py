#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from osc_lib import utils

from openstackclient.tests.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import snapshot


class TestSnapshot(volume_fakes.TestVolume):

    def setUp(self):
        super(TestSnapshot, self).setUp()

        self.snapshots_mock = self.app.client_manager.volume.volume_snapshots
        self.snapshots_mock.reset_mock()
        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()


class TestSnapshotCreate(TestSnapshot):

    columns = (
        'created_at',
        'description',
        'id',
        'name',
        'properties',
        'size',
        'status',
        'volume_id',
    )

    def setUp(self):
        super(TestSnapshotCreate, self).setUp()

        self.volume = volume_fakes.FakeVolume.create_one_volume()
        self.new_snapshot = volume_fakes.FakeSnapshot.create_one_snapshot(
            attrs={'volume_id': self.volume.id})

        self.data = (
            self.new_snapshot.created_at,
            self.new_snapshot.description,
            self.new_snapshot.id,
            self.new_snapshot.name,
            utils.format_dict(self.new_snapshot.metadata),
            self.new_snapshot.size,
            self.new_snapshot.status,
            self.new_snapshot.volume_id,
        )

        self.volumes_mock.get.return_value = self.volume
        self.snapshots_mock.create.return_value = self.new_snapshot
        # Get the command object to test
        self.cmd = snapshot.CreateSnapshot(self.app, None)

    def test_snapshot_create(self):
        arglist = [
            "--name", self.new_snapshot.name,
            "--description", self.new_snapshot.description,
            "--force",
            self.new_snapshot.volume_id,
        ]
        verifylist = [
            ("name", self.new_snapshot.name),
            ("description", self.new_snapshot.description),
            ("force", True),
            ("volume", self.new_snapshot.volume_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.snapshots_mock.create.assert_called_with(
            self.new_snapshot.volume_id,
            force=True,
            name=self.new_snapshot.name,
            description=self.new_snapshot.description
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_snapshot_create_without_name(self):
        arglist = [
            self.new_snapshot.volume_id,
            "--description", self.new_snapshot.description,
            "--force"
        ]
        verifylist = [
            ("volume", self.new_snapshot.volume_id),
            ("description", self.new_snapshot.description),
            ("force", True)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.snapshots_mock.create.assert_called_with(
            self.new_snapshot.volume_id,
            force=True,
            name=None,
            description=self.new_snapshot.description
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestSnapshotDelete(TestSnapshot):

    snapshot = volume_fakes.FakeSnapshot.create_one_snapshot()

    def setUp(self):
        super(TestSnapshotDelete, self).setUp()

        self.snapshots_mock.get.return_value = self.snapshot
        self.snapshots_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = snapshot.DeleteSnapshot(self.app, None)

    def test_snapshot_delete(self):
        arglist = [
            self.snapshot.id
        ]
        verifylist = [
            ("snapshots", [self.snapshot.id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.snapshots_mock.delete.assert_called_with(self.snapshot.id)
        self.assertIsNone(result)


class TestSnapshotList(TestSnapshot):

    volume = volume_fakes.FakeVolume.create_one_volume()
    snapshots = volume_fakes.FakeSnapshot.create_snapshots(
        attrs={'volume_id': volume.name}, count=3)

    columns = [
        "ID",
        "Name",
        "Description",
        "Status",
        "Size"
    ]
    columns_long = columns + [
        "Created At",
        "Volume",
        "Properties"
    ]

    data = []
    for s in snapshots:
        data.append((
            s.id,
            s.name,
            s.description,
            s.status,
            s.size,
        ))
    data_long = []
    for s in snapshots:
        data_long.append((
            s.id,
            s.name,
            s.description,
            s.status,
            s.size,
            s.created_at,
            s.volume_id,
            utils.format_dict(s.metadata),
        ))

    def setUp(self):
        super(TestSnapshotList, self).setUp()

        self.volumes_mock.list.return_value = [self.volume]
        self.snapshots_mock.list.return_value = self.snapshots
        # Get the command to test
        self.cmd = snapshot.ListSnapshot(self.app, None)

    def test_snapshot_list_without_options(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
            ("long", False)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_snapshot_list_with_options(self):
        arglist = ["--long"]
        verifylist = [("long", True), ('all_projects', False)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_snapshot_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('long', False),
            ('all_projects', True)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestSnapshotSet(TestSnapshot):

    snapshot = volume_fakes.FakeSnapshot.create_one_snapshot()

    def setUp(self):
        super(TestSnapshotSet, self).setUp()

        self.snapshots_mock.get.return_value = self.snapshot
        self.snapshots_mock.set_metadata.return_value = None
        self.snapshots_mock.update.return_value = None
        # Get the command object to mock
        self.cmd = snapshot.SetSnapshot(self.app, None)

    def test_snapshot_set(self):
        arglist = [
            "--name", "new_snapshot",
            "--property", "x=y",
            "--property", "foo=foo",
            self.snapshot.id,
        ]
        new_property = {"x": "y", "foo": "foo"}
        verifylist = [
            ("name", "new_snapshot"),
            ("property", new_property),
            ("snapshot", self.snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            "name": "new_snapshot",
        }
        self.snapshots_mock.update.assert_called_with(
            self.snapshot.id, **kwargs)
        self.snapshots_mock.set_metadata.assert_called_with(
            self.snapshot.id, new_property
        )
        self.assertIsNone(result)

    def test_snapshot_set_state_to_error(self):
        arglist = [
            "--state", "error",
            self.snapshot.id
        ]
        verifylist = [
            ("state", "error"),
            ("snapshot", self.snapshot.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.snapshots_mock.reset_state.assert_called_with(
            self.snapshot.id, "error")
        self.assertIsNone(result)


class TestSnapshotShow(TestSnapshot):

    columns = (
        'created_at',
        'description',
        'id',
        'name',
        'properties',
        'size',
        'status',
        'volume_id',
    )

    def setUp(self):
        super(TestSnapshotShow, self).setUp()

        self.snapshot = volume_fakes.FakeSnapshot.create_one_snapshot()

        self.data = (
            self.snapshot.created_at,
            self.snapshot.description,
            self.snapshot.id,
            self.snapshot.name,
            utils.format_dict(self.snapshot.metadata),
            self.snapshot.size,
            self.snapshot.status,
            self.snapshot.volume_id,
        )

        self.snapshots_mock.get.return_value = self.snapshot
        # Get the command object to test
        self.cmd = snapshot.ShowSnapshot(self.app, None)

    def test_snapshot_show(self):
        arglist = [
            self.snapshot.id
        ]
        verifylist = [
            ("snapshot", self.snapshot.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.snapshots_mock.get.assert_called_with(self.snapshot.id)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestSnapshotUnset(TestSnapshot):

    snapshot = volume_fakes.FakeSnapshot.create_one_snapshot()

    def setUp(self):
        super(TestSnapshotUnset, self).setUp()

        self.snapshots_mock.get.return_value = self.snapshot
        self.snapshots_mock.delete_metadata.return_value = None
        # Get the command object to mock
        self.cmd = snapshot.UnsetSnapshot(self.app, None)

    def test_snapshot_unset(self):
        arglist = [
            "--property", "foo",
            self.snapshot.id,
        ]
        verifylist = [
            ("property", ["foo"]),
            ("snapshot", self.snapshot.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.snapshots_mock.delete_metadata.assert_called_with(
            self.snapshot.id, ["foo"]
        )
        self.assertIsNone(result)
